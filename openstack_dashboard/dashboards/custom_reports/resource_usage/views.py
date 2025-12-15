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

import logging

from django.utils.translation import gettext_lazy as _
from django.views import generic

from horizon import views

from openstack_dashboard import api

LOG = logging.getLogger(__name__)


class IndexView(views.HorizonTemplateView):
    template_name = 'custom_reports/resource_usage/index.html'
    page_title = _("资源使用报告")

    def _normalize_quota(self, value):
        """
        Normalize quota value to handle unlimited quotas.
        
        OpenStack returns -1 or 0 for unlimited quotas, which would cause
        division by zero errors in templates. Convert these to a large number
        for display purposes.
        
        Args:
            value: Raw quota value from OpenStack API
            
        Returns:
            int: Normalized quota value (minimum 1 to avoid division errors)
        """
        if value is None or value <= 0:
            # Use a large number to represent "unlimited" in calculations
            # while avoiding actual infinity for chart display
            return 999999
        return value

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get compute limits (includes both quotas and usage)
            limits = api.nova.tenant_absolute_limits(self.request, reserved=False)
            
            # Get compute quotas for additional info
            tenant_id = self.request.user.tenant_id
            compute_quotas = api.nova.tenant_quota_get(self.request, tenant_id)
            
            # Prepare data for charts
            # Note: Quota limits are normalized to handle unlimited quotas (-1 or 0)
            quota_data = {
                'compute': {
                    'instances': {
                        'used': limits.get('totalInstancesUsed', 0),
                        'limit': self._normalize_quota(limits.get('maxTotalInstances', 0)),
                    },
                    'cores': {
                        'used': limits.get('totalCoresUsed', 0),
                        'limit': self._normalize_quota(limits.get('maxTotalCores', 0)),
                    },
                    'ram': {
                        'used': limits.get('totalRAMUsed', 0),
                        'limit': self._normalize_quota(limits.get('maxTotalRAMSize', 0)),
                    },
                }
            }
            
            context['quota_data'] = quota_data
            context['has_data'] = True
            
        except Exception as e:
            LOG.error("Error retrieving quota data: %s", e)
            import traceback
            LOG.error("Traceback: %s", traceback.format_exc())
            context['has_data'] = False
            context['error_message'] = _("Unable to retrieve quota information: %s") % str(e)
        
        return context
