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
"""Create SQLAlchenmy and Schema managers.

These will get initialized by the application using the models
"""
import pg8000
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sql_versioning import versioned_session
from sqlalchemy import event

from .custom_query import CustomQuery


def handle_disconnect_event(engine):
    """Fixes issue where a socket closes throws exception Broken Pipe that causes network error."""

    @event.listens_for(engine, "handle_disconnect")
    def _handle_disconnect(dialect, connection, exc, **kw):
        # Tell SQLAlchemy this exception means "connection is dead" → invalidate it
        if isinstance(exc, (pg8000.exceptions.InterfaceError, BrokenPipeError)):
            return True
        return False


# by convention in the Flask community these are lower case,
# whereas pylint wants them upper case
ma = Marshmallow()  # pylint: disable=invalid-name
db = SQLAlchemy(query_class=CustomQuery)  # pylint: disable=invalid-name
versioned_session(db.session)
