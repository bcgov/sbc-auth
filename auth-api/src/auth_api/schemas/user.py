# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Manager for user schema and export."""

from marshmallow import fields

from auth_api.models import User as UserModel

from .base_schema import BaseSchema


class UserSchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the User model."""

    class Meta(BaseSchema.Meta):  # pylint: disable=too-few-public-methods
        """Maps all of the User fields to a default schema."""

        model = UserModel
        exclude = (
            'orgs',
            'is_terms_of_use_accepted',
            'terms_of_use_accepted_version',
            'terms_of_use_version'
        )

    user_terms = fields.Method('get_user_terms_object')
    contacts = fields.Pluck('ContactLinkSchema', 'contact', many=True)

    def get_user_terms_object(self, obj):
        """Map terms properties into nested object."""
        return {
            'isTermsOfUseAccepted': obj.is_terms_of_use_accepted,
            'termsOfUseAcceptedVersion': obj.terms_of_use_accepted_version
        }
