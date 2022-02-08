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
"""This manages the settings associated with the user.

It defines the settings available for the user which can be displayed in the header menu
"""


class UserSettings():  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    This is the User Settings model.

    the structure of the model is not well defined.so going for this now.
    In general , it should items info and a way to access them [url] which user has access to.
    Can extended to product which user has access to.
    """

    def __init__(self, id_, label, urlorigin, urlpath, type_, account_type=None,  # pylint: disable=too-many-arguments
                 account_status=None, product_settings=None, additional_label=None):
        """Return a usersettings."""
        self.id = id_
        self.label = label
        self.urlorigin = urlorigin
        self.urlpath = urlpath
        self.type = type_
        self.account_type = account_type
        self.account_status = account_status
        self.product_settings = product_settings
        self.additional_label = additional_label  # used for org branch name
