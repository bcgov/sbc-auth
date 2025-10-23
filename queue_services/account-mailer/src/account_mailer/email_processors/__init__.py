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
"""The Events Listener service.

This module is the service worker for applying filings to the Business Database structure.
"""

import os
from pathlib import Path


def generate_template(template_path: str, template_file_name: str) -> str:
    """Substitute template parts in main template.

    Template parts are marked by [[partname.html]] in templates.

    This functionality is restricted by:
    - markup must be exactly [[partname.html]] and have no extra spaces around file name
    - template parts can only be one level deep, ie: this rudimentary framework does not handle nested template
    parts. There is no recursive search and replace.
    """
    template_parts = [
        "business-dashboard-link",
        "footer",
        "header",
        "initiative-notice",
        "logo",
        "style",
        "fonts",
        "bc_logo_img",
        "bc_registry_logo_img",
        "whitespace-16px",
        "whitespace-24px",
    ]

    template_code = Path(f"{template_path}/{template_file_name}.html").read_text()  # pylint: disable=W1514

    # substitute template parts - marked up by [[filename]]
    for template_part in template_parts:
        template_part_path = Path(f"{template_path}/common/{template_part}.html")
        if os.path.exists(template_part_path) and os.path.getsize(template_part_path) > 0:
            template_part_code = template_part_path.read_text()  # pylint: disable=W1514
            template_code = template_code.replace(f"[[{template_part}.html]]", template_part_code)

    return template_code
