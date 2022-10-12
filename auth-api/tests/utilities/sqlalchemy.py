# Copyright © 2022 Province of British Columbia
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
"""Utility to remove event listeners for models."""
import ctypes
from sqlalchemy import event


def clear_event_listeners(model):
    """Remove event listeners for a model."""
    keys = [k for k in event.registry._key_to_collection if k[0] == id(model)]
    for key in keys:
        target = model
        identifier = key[1]
        fn = ctypes.cast(key[2], ctypes.py_object).value  # get function by id
        event.remove(target, identifier, fn)
