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

from django.db import models


class TenantResourceSnapshot(models.Model):
    """租户资源使用快照，用于历史趋势和报表."""

    tenant_id = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 计算资源
    instances_used = models.IntegerField()
    instances_limit = models.IntegerField()
    cores_used = models.IntegerField()
    cores_limit = models.IntegerField()
    ram_used = models.IntegerField()       # MB
    ram_limit = models.IntegerField()

    # 存储资源
    volumes_used = models.IntegerField()
    volumes_limit = models.IntegerField()
    gigabytes_used = models.IntegerField()
    gigabytes_limit = models.IntegerField()
    snapshots_used = models.IntegerField()
    snapshots_limit = models.IntegerField()

    # 网络资源
    networks_used = models.IntegerField()
    networks_limit = models.IntegerField()
    floatingips_used = models.IntegerField()
    floatingips_limit = models.IntegerField()
    routers_used = models.IntegerField()
    routers_limit = models.IntegerField()
    security_groups_used = models.IntegerField()
    security_groups_limit = models.IntegerField()

    class Meta:
        db_table = 'tenant_resource_snapshot'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tenant_id} @ {self.created_at}"
