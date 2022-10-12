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
"""Exposes all of the Services used in the API."""
from .activity_log import ActivityLog
from .activity_log_publisher import ActivityLogPublisher
from .affidavit import Affidavit
from .affiliation import Affiliation
from .api_gateway import ApiGateway
from .codes import Codes
from .contact import Contact
from .documents import Documents
from .entity import Entity
from .invitation import Invitation
from .membership import Membership
from .minio import MinioService
from .org import Org
from .permissions import Permissions
from .products import Product
from .reset import ResetTestData
from .task import Task
from .user import User
from .user_settings import UserSettings
from .flags import Flags

flags = Flags()
