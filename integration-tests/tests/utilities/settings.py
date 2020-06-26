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
"""testing config."""
import glob
import json
import os
import random
from functools import lru_cache
from itertools import repeat
from typing import Dict, List

import pandas as pd
from pydantic import BaseModel, BaseSettings


class UserInfo(BaseModel):
    """  """

    username: str = ''
    password: str = ''


class TestingSettings(BaseSettings):
    """API settings."""

    ROOT_URL: str = 'https://dev.bcregistry.ca/business'
    BCSC_USERS: List[UserInfo] = list()
    BCOL_USERS: List[UserInfo] = list()
    BCEID_USERS: List[UserInfo] = list()
    ACCESS_SETUP: Dict = {
            "BASIC": {
                "BCSC": {"ADMIN": 1, "COORDINATOR": 0},
                "BCEID": {"ADMIN": 0, "COORDINATOR": 0},
                "BUSINESS": {"cooperatives": 1, "benefitcompany": 1, "namerequest": 1},
                "PAYMENT": {"transaction": 2}
            },
            "PREMIUM": {
                "BCSC": {"ADMIN": 1},
                "BCEID": {"ADMIN": 0, "COORDINATOR": 0},
                "BUSINESS": {"cooperatives": 1, "benefitcompany": 1, "namerequest": 1},
                "PAYMENT": {"transaction": 2}
            },
            "STAFF": {
                "IDIR": {"STAFF_ADMIN": 1, "STAFF": 1},
                "ANONYMOUS": {"ADMIN": 1, "USER": 1},
                "BUSINESS": {"cooperatives": 1, "benefitcompany": 0, "namerequest": 0},
                "PAYMENT": {"transaction": 2}
            },
            "ANONYMOUS": {
                "ANONYMOUS": {"ADMIN": 1, "USER": 1}
            }
           }
    PAYBC_CREDITCARD: str = ''
    PAYBC_CREDITCARD_CVV: str = ''

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        env_file = '.env'
        case_sensitive = True


@lru_cache()
def get_settings() -> TestingSettings:
    """Get settings."""
    return TestingSettings()  # reads variables from environment


class PathSetting(BaseModel):
    """  """

    ADMIN: str = f'{get_settings().ROOT_URL}/auth/signin/bcsc'
    COORDINATOR: str = f'{get_settings().ROOT_URL}/auth/validatetoken'
    USER: str = f'{get_settings().ROOT_URL}/auth/validatetoken'
    PAYMENT_RETURN: str = f'{get_settings().ROOT_URL}/auth/returnpayment'


@lru_cache()
def get_path_settings() -> PathSetting:
    """Get Path settings."""
    return PathSetting()  # reads variables from environment


def setup_access_data(account_type: str, access_type: list) -> list:
    """Get login user account from configuration."""
    account_type = get_settings().ACCESS_SETUP[account_type]

    access_data: list = []

    for access_name in access_type:
        users: list = getattr(get_settings(), f'{access_name}_USERS')
        # setup a user account list that include all of test accounts need for current round of testing.
        pick_users: list = random.sample(users, sum(account_type[access_name].values()))
        user_index: int = 0
        for name, value in account_type[access_name].items():
            path: str = getattr(get_path_settings(), name)
            # setup pytest parametrize list
            for _ in repeat(None, value):
                user: UserInfo = pick_users[user_index]
                login = {'loginAs': name, 'path': path, 'username': user.username, 'password': user.password}
                access_data.append(login)
                user_index = user_index + 1

    return access_data


def load_data_from_csv():
    """Load all the test data from csv files.  """
    filenames = glob.glob(os.path.dirname(os.path.dirname(__file__)) + f'/csv/**/*.csv')
    dataframe = {}
    for f in filenames:
        base = os.path.basename(f)
        dataframe[os.path.splitext(base)[0]] = pd.read_csv(f, dtype=str, index_col=False)
    return dataframe


def get_test_data(test_data):
    """Get test data from csv dataframe and pick a random record to convert to Dict."""
    input_data = test_data.to_dict(orient='records')

    return random.sample(input_data, 1)[0]
