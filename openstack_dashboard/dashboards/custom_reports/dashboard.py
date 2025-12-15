# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.utils.translation import gettext_lazy as _

import horizon


class CustomReports(horizon.Dashboard):
    name = _("自定义报表")
    slug = "custom_reports"
    panels = ('comprehensive_overview', 'resource_usage',)
    default_panel = 'comprehensive_overview'
    policy_rules = (("compute", "compute:get_all"),)


horizon.register(CustomReports)
