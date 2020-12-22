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
"""Callbacks and signal trapping used in the main loop."""
from flask import current_app


async def error_cb(e):
    """Emit error message to the log stream."""
    current_app.logger.error(e)
    raise e


async def closed_cb():
    """Exit the session after the NATS connection is closed."""
    current_app.logger.info('Connection to NATS is closed.')
    # my_loop = asyncio.get_running_loop()
    # await asyncio.sleep(0.1, loop=my_loop)
    # my_loop.stop()
