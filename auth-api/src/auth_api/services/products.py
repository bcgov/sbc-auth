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
from sqlalchemy import and_, case, func, literal, or_
from sqlalchemy.exc import SQLAlchemyError

from auth_api.models.dataclass import Activity, KeycloakGroupSubscription, ProductReviewTask
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.services.keycloak import KeycloakService
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import ProductCode as ProductCodeModel
from auth_api.models import ProductSubscription as ProductSubscriptionModel
from auth_api.models import User as UserModel
from auth_api.models import db
from auth_api.schemas import ProductCodeSchema
from auth_api.services.user import User as UserService
from auth_api.utils.constants import BCOL_PROFILE_PRODUCT_MAP
from auth_api.utils.enums import (
    AccessType, ActivityAction, KeycloakGroupActions, OrgType, ProductCode, ProductSubscriptionStatus, Status,
    TaskAction, TaskRelationshipStatus, TaskRelationshipType, TaskStatus)
from auth_api.utils.user_context import UserContext, user_context

from ..utils.account_mailer import publish_to_mailer
from ..utils.cache import cache
from ..utils.roles import CLIENT_ADMIN_ROLES, CLIENT_AUTH_ROLES, PREMIUM_ORG_TYPES, STAFF
from .activity_log_publisher import ActivityLogPublisher
from .authorization import check_auth
from .task import Task as TaskService

QUALIFIED_SUPPLIER_PRODUCT_CODES = [ProductCode.MHR_QSLN.value, ProductCode.MHR_QSHD.value,
                                    ProductCode.MHR_QSHM.value]


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
            current_app.logger.info('Error on building cache %s', e)

    @staticmethod
    def find_product_type_by_code(code: str) -> str:
        """Find Product Type."""
        code_from_cache = cache.get(code)
        if code_from_cache:
            return code_from_cache
        product_code_model: ProductCodeModel = ProductCodeModel.find_by_code(code)
        return getattr(product_code_model, 'type_code', '')

    @staticmethod
    def create_product_subscription(org_id, subscription_data: Dict[str, Any],  # pylint: disable=too-many-locals
                                    is_new_transaction: bool = True, skip_auth=False):
        """Create product subscription for the user.

        create product subscription first
        create the product role next if roles are given
        """
        org: OrgModel = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        # Check authorization for the user
        if not skip_auth:
            check_auth(one_of_roles=(*CLIENT_ADMIN_ROLES, STAFF), org_id=org_id)

        subscriptions_list = subscription_data.get('subscriptions')
        for subscription in subscriptions_list:
            product_code = subscription.get('productCode')
            existing_product_subscriptions = ProductSubscriptionModel.find_by_org_id_product_code(org_id, product_code)
            if existing_product_subscriptions:
                raise BusinessException(Error.PRODUCT_SUBSCRIPTION_EXISTS, None)
            product_model: ProductCodeModel = ProductCodeModel.find_by_code(product_code)
            if product_model:
                # Check if product requires system admin, if yes abort
                if product_model.need_system_admin:
                    check_auth(system_required=True, org_id=org_id)
                # Check if product needs premium account, if yes skip and continue.
                if product_model.premium_only and org.type_code not in PREMIUM_ORG_TYPES:
                    continue

                subscription_status = Product.find_subscription_status(org, product_model)
                product_subscription = Product._subscribe_and_publish_activity(org_id,
                                                                               product_code,
                                                                               subscription_status,
                                                                               product_model.description)

                # If there is a linked product, add subscription to that too.
                # This is to handle cases where Names and Business Registry is combined together.
                if product_model.linked_product_code:
                    Product._subscribe_and_publish_activity(org_id,
                                                            product_model.linked_product_code,
                                                            subscription_status,
                                                            product_model.description)

                # If there is a parent product, add subscription to that to
                # This is to satisfy any preceding subscriptions required
                if product_model.parent_code:
                    Product._update_parent_subscription(org_id, product_model, subscription_status)

                # create a staff review task for this product subscription if pending status
                if subscription_status == ProductSubscriptionStatus.PENDING_STAFF_REVIEW.value:
                    user = UserModel.find_by_jwt_token()
                    external_source_id = subscription.get('externalSourceId')
                    Product._create_review_task(ProductReviewTask(org_id=org.id,
                                                                  org_name=org.name,
                                                                  product_code=product_subscription.product_code,
                                                                  product_description=product_model.description,
                                                                  product_subscription_id=product_subscription.id,
                                                                  user_id=user.id,
                                                                  external_source_id=external_source_id
                                                                  ))

            else:
                raise BusinessException(Error.DATA_NOT_FOUND, None)

        if is_new_transaction:  # Commit the transaction if it's a new transaction
            db.session.commit()

        return Product.get_all_product_subscription(org_id=org_id, skip_auth=True)

    @staticmethod
    def _update_parent_subscription(org_id, sub_product_model, subscription_status):
        parent_code = sub_product_model.parent_code
        parent_product_model: ProductCodeModel = ProductCodeModel.find_by_code(parent_code)
        existing_parent_sub = ProductSubscriptionModel \
            .find_by_org_id_product_code(org_id, parent_code)

        # Parent sub does not exist create it and return
        if not existing_parent_sub:
            Product._subscribe_and_publish_activity(org_id,
                                                    sub_product_model.parent_code,
                                                    subscription_status,
                                                    parent_product_model.description)
            return

        # Parent sub exists and is not active - update the status
        if existing_parent_sub.status_code != ProductSubscriptionStatus.ACTIVE.value:
            existing_parent_sub.status_code = subscription_status
            existing_parent_sub.flush()

    @staticmethod
    def _subscribe_and_publish_activity(org_id: int, product_code: str, status_code: str,
                                        product_model_description: str):
        subscription = ProductSubscriptionModel(org_id=org_id, product_code=product_code, status_code=status_code)\
            .flush()
        if status_code == ProductSubscriptionStatus.ACTIVE.value:
            ActivityLogPublisher.publish_activity(Activity(org_id,
                                                           ActivityAction.ADD_PRODUCT_AND_SERVICE.value,
                                                           name=product_model_description))
        return subscription

    @staticmethod
    def _create_review_task(review_task: ProductReviewTask):
        task_type = review_task.product_description
        action_type = TaskAction.QUALIFIED_SUPPLIER_REVIEW.value \
            if review_task.product_code in QUALIFIED_SUPPLIER_PRODUCT_CODES \
            else TaskAction.PRODUCT_REVIEW.value

        task_info = {'name': review_task.org_name,
                     'relationshipId': review_task.product_subscription_id,
                     'relatedTo': review_task.user_id,
                     'dateSubmitted': datetime.today(),
                     'relationshipType': TaskRelationshipType.PRODUCT.value,
                     'type': task_type,
                     'action': action_type,
                     'status': TaskStatus.OPEN.value,
                     'accountId': review_task.org_id,
                     'relationship_status': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value,
                     'externalSourceId': review_task.external_source_id
                     }
        TaskService.create_task(task_info, False)

    @staticmethod
    def find_subscription_status(org, product_model):
        """Return the subscriptions status based on org type."""
        # GOVM accounts has default active subscriptions
        skip_review_types = [AccessType.GOVM.value]
        if product_model.need_review:
            return ProductSubscriptionStatus.ACTIVE.value if (org.access_type in skip_review_types) \
                else ProductSubscriptionStatus.PENDING_STAFF_REVIEW.value
        return ProductSubscriptionStatus.ACTIVE.value

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
                        (existing_sub := subscription).status_code != ProductSubscriptionStatus.ACTIVE.value:
                    existing_sub.status_code = ProductSubscriptionStatus.ACTIVE.value
                    existing_sub.flush()

    @staticmethod
    @user_context
    def get_products(include_hidden: bool = True, staff_check: bool = True, **kwargs):
        """Get a list of all products."""
        user_from_context: UserContext = kwargs['user_context']
        if staff_check:
            include_hidden = user_from_context.is_staff() and include_hidden
        products = ProductCodeModel.get_all_products() if include_hidden \
            else ProductCodeModel.get_visible_products()
        return ProductCodeSchema().dump(products, many=True)

    @staticmethod
    @user_context
    def get_all_product_subscription(org_id, skip_auth=False, **kwargs):
        """Get a list of all products with their subscription details."""
        user_from_context: UserContext = kwargs['user_context']
        org = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        # Check authorization for the user
        if not skip_auth:
            check_auth(one_of_roles=(*CLIENT_AUTH_ROLES, STAFF), org_id=org_id)

        product_subscriptions: List[ProductSubscriptionModel] = ProductSubscriptionModel.find_by_org_ids([org_id])
        subscriptions_dict = {x.product_code: x.status_code for x in product_subscriptions}

        # Include hidden products only for staff and SBC staff
        include_hidden = user_from_context.is_staff() \
            or org.type_code == OrgType.SBC_STAFF.value \
            or kwargs.get('include_hidden', False)

        products = Product.get_products(include_hidden=include_hidden, staff_check=False)
        for product in products:
            product['subscriptionStatus'] = subscriptions_dict.get(product.get('code'),
                                                                   ProductSubscriptionStatus.NOT_SUBSCRIBED.value)

        return products

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

        product_model: ProductCodeModel = ProductCodeModel.find_by_code(product_subscription.product_code)
        # Find admin email addresses
        admin_emails = UserService.get_admin_emails_for_org(org_id)
        if admin_emails != '':
            Product.send_approved_product_subscription_notification(admin_emails, product_model.description,
                                                                    product_subscription.status_code)
        else:
            # continue but log error
            current_app.logger.error('No admin email record for org id %s', org_id)
        if is_approved:
            ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.ADD_PRODUCT_AND_SERVICE.value,
                                                           name=product_model.description))

        if product_model.parent_code:
            Product.approve_reject_parent_subscription(product_model.parent_code, is_approved, org_id,
                                                       is_new_transaction)

        current_app.logger.debug('>update_task_product ')

    @staticmethod
    def approve_reject_parent_subscription(parent_product_code: int, is_approved: bool, org_id: int,
                                           is_new_transaction: bool = True):
        """Approve or reject Parent Product Subscription."""
        current_app.logger.debug('<approve_reject_parent_subscription ')

        product_subscription: ProductSubscriptionModel = ProductSubscriptionModel.find_by_org_id_product_code(
            org_id=org_id,
            product_code=parent_product_code
        )

        # There is no parent product subscription
        if not product_subscription:
            return

        status = product_subscription.status_code

        # Subscription is already Active
        if status == ProductSubscriptionStatus.ACTIVE.value:
            return

        if is_approved:
            product_subscription.status_code = ProductSubscriptionStatus.ACTIVE.value
        else:
            product_subscription.status_code = ProductSubscriptionStatus.REJECTED.value

        product_subscription.flush()
        if is_new_transaction:  # Commit the transaction if it's a new transaction
            db.session.commit()

        product_model: ProductCodeModel = ProductCodeModel.find_by_code(parent_product_code)
        # Find admin email addresses
        admin_emails = UserService.get_admin_emails_for_org(org_id)
        if admin_emails != '':
            Product.send_approved_product_subscription_notification(admin_emails, product_model.description,
                                                                    status)
        else:
            # continue but log error
            current_app.logger.error('No admin email record for org id %s', org_id)
        if is_approved:
            ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.ADD_PRODUCT_AND_SERVICE.value,
                                                           name=product_model.description))
        current_app.logger.debug('>approve_reject_parent_subscription ')

    @staticmethod
    def send_approved_product_subscription_notification(receipt_admin_emails, product_name,
                                                        product_subscription_status: ProductSubscriptionStatus):
        """Send Approved product subscription notification to the user."""
        current_app.logger.debug('<send_approved_prod_subscription_notification')

        if product_subscription_status == ProductSubscriptionStatus.ACTIVE.value:
            notification_type = 'prodPackageApprovedNotification'
        else:
            notification_type = 'prodPackageRejectedNotification'
        data = {
            'productName': product_name,
            'emailAddresses': receipt_admin_emails
        }
        try:
            publish_to_mailer(notification_type, data=data)
            current_app.logger.debug('<send_approved_prod_subscription_notification>')
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_approved_prod_subscription_notification failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e

    @staticmethod
    def get_users_product_subscriptions_kc_groups(user_ids: List[int]) -> List[KeycloakGroupSubscription]:
        """Generate Keycloak Group Subscriptions."""
        ps_max_subquery = db.session.query(
            func.max(ProductSubscriptionModel.id).label('id'),
            ProductSubscriptionModel.product_code,
            ProductSubscriptionModel.org_id
        ) \
            .group_by(ProductSubscriptionModel.product_code, ProductSubscriptionModel.org_id) \
            .subquery()

        m_max_subquery = db.session.query(
            func.max(MembershipModel.id).label('id'),
            MembershipModel.org_id,
            MembershipModel.user_id
        ) \
            .group_by(MembershipModel.org_id, MembershipModel.user_id) \
            .subquery()

        active_subscription_case = case(
            [
                 (and_(MembershipModel.status == Status.ACTIVE.value, ProductSubscriptionModel.status_code ==
                       ProductSubscriptionStatus.ACTIVE.value), 1),
            ],
            else_=0
        )

        user_subscriptions = db.session.query(UserModel, ProductCodeModel) \
            .join(ProductCodeModel, literal(True)) \
            .outerjoin(m_max_subquery, m_max_subquery.c.user_id == UserModel.id) \
            .outerjoin(MembershipModel, MembershipModel.id == m_max_subquery.c.id) \
            .outerjoin(
            # pylint: disable=comparison-with-callable
            ps_max_subquery, ps_max_subquery.c.product_code == ProductCodeModel.code) \
            .outerjoin(ProductSubscriptionModel, ProductSubscriptionModel.id == ps_max_subquery.c.id) \
            .filter(or_(
                    ProductSubscriptionModel.org_id == MembershipModel.org_id,
                    ProductSubscriptionModel.org_id.is_(None),
                    MembershipModel.org_id.is_(None)))\
            .filter(UserModel.id.in_(user_ids)) \
            .filter(ProductCodeModel.keycloak_group.isnot(None))\
            .group_by(UserModel.id, UserModel.keycloak_guid, ProductCodeModel.code, ProductCodeModel.keycloak_group)\
            .order_by(UserModel.id, ProductCodeModel.code)\
            .with_entities(
                UserModel.id,
                UserModel.keycloak_guid,
                ProductCodeModel.code,
                ProductCodeModel.keycloak_group,
                func.sum(active_subscription_case).label('active_subscription_count')
        ).all()  # pylint: disable=comparison-with-callable

        keycloak_group_subscriptions = []
        for ups in user_subscriptions:
            action = KeycloakGroupActions.ADD_TO_GROUP.value \
                if ups.active_subscription_count > 0 else KeycloakGroupActions.REMOVE_FROM_GROUP.value
            kgs = KeycloakGroupSubscription(ups.keycloak_guid, ups.code, ups.keycloak_group, action)
            keycloak_group_subscriptions.append(kgs)

        return keycloak_group_subscriptions

    @staticmethod
    def update_users_products_keycloak_groups(user_ids: List[int]):
        """Update list of user's keycloak roles for product subscriptions."""
        current_app.logger.debug('<update_users_products_keycloak_group ')
        kc_groups = Product.get_users_product_subscriptions_kc_groups(user_ids)
        KeycloakService.add_or_remove_product_keycloak_groups(kc_groups)
        current_app.logger.debug('>update_users_products_keycloak_group ')

    @staticmethod
    def update_org_product_keycloak_groups(org_id: int):
        """Handle org level product keycloak updates."""
        user_ids = [membership.user_id for membership in MembershipModel.find_members_by_org_id(org_id)]
        Product.update_users_products_keycloak_groups(user_ids)
