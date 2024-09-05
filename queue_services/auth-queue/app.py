#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2024 Province of British Columbia
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
"""Initialize Flask app."""

import os
import sys

from auth_queue import create_app


app = create_app()

if __name__ == '__main__':
    venv_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.venv/src/sbc-auth/auth-api'))

    if venv_src_path not in sys.path:
        sys.path.insert(0, venv_src_path)
    x = sys.path

    auth_api_folder = [folder for folder in sys.path if 'auth-api' in folder][0]
    migration_path = auth_api_folder.replace('/auth-api', '/auth-api/migrations')

    # '/Users/abolyach/bc_reg/bcreg-apps/sbc-auth-fork/queue_services/auth-queue/.venv/src/sbc-auth/auth-api'


    auth_api_folder = [folder for folder in sys.path if 'auth-api' in folder][0]
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
