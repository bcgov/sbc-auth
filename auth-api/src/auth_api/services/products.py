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

from typing import Any, Dict, List

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Org as OrgModel
from auth_api.models import ProductCode as ProductCodeModel
from auth_api.models import ProductSubscription as ProductSubscriptionModel
from auth_api.models import db
from auth_api.utils.enums import ProductTypeCode, ProductCode, OrgType
from ..utils.cache import cache


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
                product_subscription = ProductSubscriptionModel(org_id=org_id, product_code=product_code).flush()
                subscriptions_model_list.append(product_subscription)
            else:
                raise BusinessException(Error.DATA_NOT_FOUND, None)

        if is_new_transaction:  # Commit the transaction if it's a new transaction
            db.session.commit()
        # TODO return something better/useful.may be return the whole model from db
        return subscriptions_model_list

    @staticmethod
    def create_default_product_subscriptions(org: OrgModel, is_new_transaction: bool = True):
        """Create default product subscriptions for the account."""
        internal_product_codes = ProductCodeModel.find_by_type_code(type_code=ProductTypeCode.INTERNAL.value)
        for product_code in internal_product_codes:
            # Add PPR only if the account is premium.
            if product_code.code == ProductCode.PPR.value:
                if org.type_code == OrgType.PREMIUM.value:
                    ProductSubscriptionModel(org_id=org.id, product_code=product_code.code).flush()
            else:
                ProductSubscriptionModel(org_id=org.id, product_code=product_code.code).flush()
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
                        'name': product.description,
                        'description': product_config.get('description'),
                        'url': product_config.get('url'),
                        'type': product.type_code,
                        'mdiIcon': product_config.get('mdiIcon')
                    })
        return merged_product_infos
