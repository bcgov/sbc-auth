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

from typing import Any, Dict

from flask import current_app

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Org as OrgModel
from auth_api.models import ProductCode as ProductCodeModel
from auth_api.models import ProductRoleCode as ProductRoleCodeModel
from auth_api.models import ProductSubscription as ProductSubscriptionModel
from auth_api.models import ProductSubscriptionRole as ProductSubscriptionRoleModel
from auth_api.models import db


class Product:
    """Manages all aspects of Products data.

    This service manages creating, updating, and retrieving products and product subscriptions.
    """

    @staticmethod
    def create_product_subscription(org_id, subscription_data: Dict[str, Any], is_new_transaction: bool = True):
        """Create product subscription for the user.

        create product subscription first
        create the product role next if roles are given
        """
        org = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        subscriptions_list = subscription_data.get('subscriptions')
        # just used for returning all the models.. not ideal..
        # todo remove this and may be return the subscriptions from db
        subscriptions_model_list = []
        for subscription in subscriptions_list:
            product_code = subscription.get('productCode')
            product = ProductCodeModel.find_by_code(product_code)
            if product:
                product_subscription = ProductSubscriptionModel(org_id=org_id, product_code=product_code).save()
                subscriptions_model_list.append(product_subscription)
            else:
                raise BusinessException(Error.DATA_NOT_FOUND, None)

            Product._create_roles(is_new_transaction, product_code, product_subscription, subscription)

        # TODO return something better/useful.may be return the whole model from db
        return subscriptions_model_list

    @staticmethod
    def _create_roles(is_new_transaction, product_code, product_subscription, subscription):
        """Create Product Roles."""
        if subscription.get('productRoles'):
            for role in subscription.get('productRoles'):
                product_role_code = ProductRoleCodeModel.find_by_code_and_product_code(role, product_code)
                if product_role_code:
                    ProductSubscriptionRoleModel(product_subscription_id=product_subscription.id,
                                                 product_role_id=product_role_code.id).save()
        else:  # empty product roles ;give subscription to everything
            product_roles = ProductRoleCodeModel.find_all_roles_by_product_code(product_code)
            obj = []
            for role in product_roles:
                obj.append(ProductSubscriptionRoleModel(product_subscription_id=product_subscription.id,
                                                        product_role_id=role.id))
            db.session.bulk_save_objects(obj)

            if is_new_transaction:  # Commit the transaction if it's a new transaction
                db.session.commit()

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
                        'name': product.desc,
                        'description': product_config.get('description'),
                        'url': product_config.get('url'),
                        'type': product.type_code,
                        'mdiIcon': product_config.get('mdiIcon')
                    })
        return merged_product_infos
