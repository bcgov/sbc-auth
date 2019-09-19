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
"""Function to create database."""

import contextlib
import os
import sys

import sqlalchemy
import sqlalchemy.exc

from config import ProdConfig

DB_ADMIN_PASSWORD = os.getenv('DB_ADMIN_PASSWORD', None)

if not hasattr(ProdConfig, 'DB_NAME') or not DB_ADMIN_PASSWORD:
    print("Unable to create database.", sys.stdout)
    sys.exit(-1)

DATABASE_URI = 'postgresql://postgres:{password}@{host}:{port}/{name}'.format(
    password=DB_ADMIN_PASSWORD,
    host=ProdConfig.DB_HOST,
    port=int(ProdConfig.DB_PORT),
    name='postgres',
)

with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
    with sqlalchemy.create_engine(
            DATABASE_URI,
            isolation_level='AUTOCOMMIT'
    ).connect() as connection:
        DB_NAME = ProdConfig.DB_NAME
        connection.execute(f'CREATE DATABASE {DB_NAME}')
