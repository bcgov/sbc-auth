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
"""This manages a Business Size Code master records.

It defines the size of business the account is primarily doing.
"""

from .base_model import BaseCodeModel


class BusinessSizeCode(BaseCodeModel):  # pylint: disable=too-few-public-methods
    """Business Type Code to store all the available business sizes to add to the account.

    That is supported by auth system.
    """

    __tablename__ = "business_size_codes"
