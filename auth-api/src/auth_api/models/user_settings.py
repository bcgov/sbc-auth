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


class UserSettings():  # pylint: disable=too-few-public-methods
    """This is the User Settings model

    the structure of the model is not well defined.so going for this now.
    In general , it should items info and a way to access them [url] which user has access to.
    Can extended to product which user has access to.
    ."""

    def __init__(self, id_, label, url_origin, url_path, type_):
        self.id_ = id_
        self.label = label
        self.url_origin = url_origin
        self.url_path = url_path
        self.type = type_
