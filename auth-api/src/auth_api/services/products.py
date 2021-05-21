# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Service for managing Product and Product Subscription data."""
from datetime import datetime
from typing import Any, Dict, List

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Org as OrgModel
from auth_api.models import ProductCode as ProductCodeModel
from auth_api.models import ProductSubscription as ProductSubscriptionModel
from auth_api.models import User as UserModel
from auth_api.models import db
from auth_api.utils.constants import BCOL_PROFILE_PRODUCT_MAP
from auth_api.utils.enums import (
    AccessType, OrgType, ProductCode, ProductSubscriptionStatus, ProductTypeCode, TaskRelationshipStatus,
    TaskRelationshipType, TaskStatus)

from ..utils.account_mailer import publish_to_mailer
from ..utils.cache import cache
from ..utils.roles import CLIENT_ADMIN_ROLES, STAFF
from .authorization import check_auth
from .task import Task as TaskService


class Product:
    """Manages all aspects of Products data.

    This service manages creating, updating, and retrieving products and product subscriptions.
    """

    @classmethod
    def build_all_products_cache(cls):
        """Build cache for all permission values."""
        try:
            product_list: List[ProductCodeModel] = ProductCodeModel.get_all_products()
            for product in product_list:
                cache.set(product.code, product.type_code)
        except SQLAlchemyError as e:
            current_app.logger.info('Error on building cache {}', e)

    @staticmethod
    def find_product_type_by_code(code: str) -> str:
        """Find Product Type."""
        code_from_cache = cache.get(code)
        if code_from_cache:
            return code_from_cache
        product_code_model: ProductCodeModel = ProductCodeModel.find_by_id(code)
        return getattr(product_code_model, 'type_code', '')

    @staticmethod
    def create_product_subscription(org_id, subscription_data: Dict[str, Any],  # pylint: disable=too-many-locals
                                    is_new_transaction: bool = True,
                                    token_info: Dict = None, skip_auth=False):
        """Create product subscription for the user.

        create product subscription first
        create the product role next if roles are given
        """
        org: OrgModel = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        # Check authorization for the user
        if not skip_auth:
            check_auth(token_info, one_of_roles=(*CLIENT_ADMIN_ROLES, STAFF), org_id=org_id)

        subscriptions_list = subscription_data.get('subscriptions')
        # just used for returning all the models.. not ideal..
        # todo remove this and may be return the subscriptions from db
        subscriptions_model_list = []
        for subscription in subscriptions_list:
            product_code = subscription.get('productCode')
            existing_product_subscriptions = ProductSubscriptionModel.find_by_org_id_product_code(org_id, product_code)
            if existing_product_subscriptions:
                raise BusinessException(Error.PRODUCT_SUBSCRIPTION_EXISTS, None)
            product_model: ProductCodeModel = ProductCodeModel.find_by_code(product_code)
            if product_model:
                subscription_status = Product.find_subscription_status(org, product_model)
                product_subscription = ProductSubscriptionModel(org_id=org_id,
                                                                product_code=product_code,
                                                                status_code=subscription_status) \
                    .flush()

                # create a staff review task for this product subscription if pending status
                if subscription_status == ProductSubscriptionStatus.PENDING_STAFF_REVIEW.value:
                    user = UserModel.find_by_jwt_token(token=token_info)
                    task_type = product_model.description
                    task_info = {'name': org.name,
                                 'relationshipId': product_subscription.id,
                                 'relatedTo': user.id,
                                 'dateSubmitted': datetime.today(),
                                 'relationshipType': TaskRelationshipType.PRODUCT.value,
                                 'type': task_type,
                                 'status': TaskStatus.OPEN.value,
                                 'accountId': org_id,
                                 'relationship_status': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
                                 }
                    do_commit = False
                    TaskService.create_task(task_info, do_commit)

                subscriptions_model_list.append(product_subscription)
            else:
                raise BusinessException(Error.DATA_NOT_FOUND, None)

        if is_new_transaction:  # Commit the transaction if it's a new transaction
            db.session.commit()
        # TODO return something better/useful.may be return the whole model from db
        return subscriptions_model_list

    @staticmethod
    def find_subscription_status(org, product_model):
        """Return the subscriptions status based on org type."""
        # GOVM accounts has default active subscriptions
        return product_model.default_subscription_status if org.access_type not in [
            AccessType.GOVM.value] else ProductSubscriptionStatus.ACTIVE.value

    @staticmethod
    def create_default_product_subscriptions(org: OrgModel, bcol_profile_flags: List[str],
                                             is_new_transaction: bool = True):
        """Create default product subscriptions for the account."""
        internal_product_codes = ProductCodeModel.find_by_type_code(type_code=ProductTypeCode.INTERNAL.value)
        for product_code in internal_product_codes:
            # Add PPR only if the account is premium.
            if product_code.code == ProductCode.PPR.value:
                if org.type_code == OrgType.PREMIUM.value:
                    ProductSubscriptionModel(org_id=org.id, product_code=product_code.code,
                                             status_code=product_code.default_subscription_status).flush()
            else:
                ProductSubscriptionModel(org_id=org.id, product_code=product_code.code,
                                         status_code=product_code.default_subscription_status).flush()
        # Now add or update the product subscription based on bcol profiles.
        Product.create_subscription_from_bcol_profile(org.id, bcol_profile_flags)
        if is_new_transaction:  # Commit the transaction if it's a new transaction
            db.session.commit()

    @staticmethod
    def create_subscription_from_bcol_profile(org_id: int, bcol_profile_flags: List[str]):
        """Create product subscription from bcol profile flags."""
        if not bcol_profile_flags:
            return
        for profile_flag in bcol_profile_flags:
            product_code = BCOL_PROFILE_PRODUCT_MAP.get(profile_flag, None)
            if product_code:
                # Check if account already have an entry for this product.
                subscription: ProductSubscriptionModel = ProductSubscriptionModel.find_by_org_id_product_code(
                    org_id, product_code
                )
                if not subscription:
                    ProductSubscriptionModel(org_id=org_id, product_code=product_code,
                                             status_code=ProductSubscriptionStatus.ACTIVE.value).flush()
                elif subscription and \
                        (existing_sub := subscription[0]).status_code != ProductSubscriptionStatus.ACTIVE.value:
                    existing_sub.status_code = ProductSubscriptionStatus.ACTIVE.value
                    existing_sub.flush()

    @staticmethod
    def get_products():
        """Get a list of all products."""
        products = ProductCodeModel.get_all_products()

        # We only want to return products that have content configured,
        # so read configuration and merge
        merged_product_infos = []
        products_config = current_app.config.get('PRODUCT_CONFIG')
        if products_config:
            for product in products:
                product_config = products_config.get(product.code)
                if product_config:
                    merged_product_infos.append({
                        'code': product.code,
                        'name': product.description,
                        'description': product_config.get('description'),
                        'url': product_config.get('url'),
                        'type': product.type_code,
                        'mdiIcon': product_config.get('mdiIcon')
                    })
        return merged_product_infos

    @staticmethod
    def get_all_product_subscription(org_id, include_internal_products=True, token_info: Dict = None, skip_auth=False):
        """Get a list of all products with their subscription details."""
        org = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        # Check authorization for the user
        if not skip_auth:
            check_auth(token_info, one_of_roles=(*CLIENT_ADMIN_ROLES, STAFF), org_id=org_id)

        product_subscriptions: List[ProductSubscriptionModel] = ProductSubscriptionModel.find_by_org_id(org_id)
        subscriptions_dict = {x.product_code: x.status_code for x in product_subscriptions}

        # We only want to return products that have content configured,
        # so read configuration and merge
        merged_product_infos = []
        products_config = current_app.config.get('PRODUCT_CONFIG')
        products: List[ProductCodeModel] = ProductCodeModel.get_all_products()
        if products:
            for product in products:
                if not include_internal_products and product.type_code == ProductTypeCode.INTERNAL.value:
                    continue
                product_config = products_config.get(product.code)
                if product_config:
                    merged_product_infos.append({
                        'code': product.code,
                        'name': product.description,
                        'description': product_config.get('description'),
                        'url': product_config.get('url'),
                        'type': product.type_code,
                        'mdiIcon': product_config.get('mdiIcon'),
                        'subscriptionStatus': subscriptions_dict.get(product.code,
                                                                     ProductSubscriptionStatus.NOT_SUBSCRIBED.value)
                    })
        return merged_product_infos

    @staticmethod
    def update_product_subscription(product_subscription_id: int, is_approved: bool, org_id: int,
                                    is_new_transaction: bool = True):
        """Update Product Subscription."""
        current_app.logger.debug('<update_task_product ')
        # Approve/Reject Product subscription
        product_subscription: ProductSubscriptionModel = ProductSubscriptionModel.find_by_id(product_subscription_id)
        if is_approved:
            product_subscription.status_code = ProductSubscriptionStatus.ACTIVE.value
        else:
            product_subscription.status_code = ProductSubscriptionStatus.REJECTED.value
        product_subscription.flush()
        if is_new_transaction:  # Commit the transaction if it's a new transaction
            db.session.commit()

        # Get the org and to get admin mail address
        org: OrgModel = OrgModel.find_by_org_id(org_id)
        # Find admin email address
        admin_email = ContactLinkModel.find_by_user_id(org.members[0].user.id).contact.email
        product_model: ProductCodeModel = ProductCodeModel.find_by_code(product_subscription.product_code)
        Product.send_approved_product_subscription_notification(admin_email, product_model.description,
                                                                product_subscription.status_code)
        current_app.logger.debug('>update_task_product ')

    @staticmethod
    def send_approved_product_subscription_notification(receipt_admin_email, product_name,
                                                        product_subscription_status: ProductSubscriptionStatus):
        """Send Approved product subscription notification to the user."""
        current_app.logger.debug('<send_approved_prod_subscription_notification')

        if product_subscription_status == ProductSubscriptionStatus.ACTIVE.value:
            notification_type = 'prodPackageApprovedNotification'
        else:
            notification_type = 'prodPackageRejectedNotification'
        data = {
            'productName': product_name,
            'emailAddresses': receipt_admin_email
        }
        try:
            publish_to_mailer(notification_type, data=data)
            current_app.logger.debug('<send_approved_prod_subscription_notification>')
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_approved_prod_subscription_notification failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e
