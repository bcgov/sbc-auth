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
"""Get metadata information from pyproject.toml
"""
import os
from importlib.metadata import metadata, version

meta = metadata(__package__ or __name__)
APP_NAME = meta["Name"]
APP_VERSION = meta["Version"]
APP_RUNNING_PROJECT = os.getenv("DEPLOYMENT_PROJECT", "local")
APP_RUNNING_ENVIRONMENT = os.getenv("DEPLOYMENT_ENV", "production")
FLASK_VERSION = version("flask")
