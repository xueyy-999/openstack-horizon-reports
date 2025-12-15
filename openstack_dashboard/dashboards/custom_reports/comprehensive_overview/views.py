# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from datetime import datetime, timedelta

from django.utils.translation import gettext_lazy as _
from django.db.models import Avg

from horizon import views

from openstack_dashboard import api
from openstack_dashboard.dashboards.custom_reports.models import TenantResourceSnapshot

LOG = logging.getLogger(__name__)


class IndexView(views.HorizonTemplateView):
    template_name = 'custom_reports/comprehensive_overview/index.html'
    page_title = _("综合资源概览")

    def _normalize_quota(self, value):
        """Normalize quota value to handle unlimited quotas."""
        if value is None or value <= 0:
            return 999999
        return value

    def _safe_divide(self, numerator, denominator):
        """Safe division to avoid division by zero."""
        if denominator == 0 or denominator is None:
            return 0
        return int((numerator / denominator) * 100)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            tenant_id = self.request.user.tenant_id
            
            # ===== 1. 计算资源 =====
            try:
                compute_limits = api.nova.tenant_absolute_limits(self.request, reserved=False)
                compute_data = {
                    'instances': {
                        'used': compute_limits.get('totalInstancesUsed', 0),
                        'limit': self._normalize_quota(compute_limits.get('maxTotalInstances', 0)),
                    },
                    'cores': {
                        'used': compute_limits.get('totalCoresUsed', 0),
                        'limit': self._normalize_quota(compute_limits.get('maxTotalCores', 0)),
                    },
                    'ram': {
                        'used': compute_limits.get('totalRAMUsed', 0),
                        'limit': self._normalize_quota(compute_limits.get('maxTotalRAMSize', 0)),
                    },
                }
                # 计算使用率
                compute_data['instances']['percent'] = self._safe_divide(
                    compute_data['instances']['used'], compute_data['instances']['limit'])
                compute_data['cores']['percent'] = self._safe_divide(
                    compute_data['cores']['used'], compute_data['cores']['limit'])
                compute_data['ram']['percent'] = self._safe_divide(
                    compute_data['ram']['used'], compute_data['ram']['limit'])
            except Exception as e:
                LOG.error("Error retrieving compute data: %s", e)
                compute_data = None
            
            # ===== 2. 存储资源 =====
            try:
                volume_limits = api.cinder.tenant_absolute_limits(self.request)
                storage_data = {
                    'volumes': {
                        'used': volume_limits.get('totalVolumesUsed', 0),
                        'limit': self._normalize_quota(volume_limits.get('maxTotalVolumes', 0)),
                    },
                    'gigabytes': {
                        'used': volume_limits.get('totalGigabytesUsed', 0),
                        'limit': self._normalize_quota(volume_limits.get('maxTotalVolumeGigabytes', 0)),
                    },
                    'snapshots': {
                        'used': volume_limits.get('totalSnapshotsUsed', 0),
                        'limit': self._normalize_quota(volume_limits.get('maxTotalSnapshots', 0)),
                    },
                }
                storage_data['volumes']['percent'] = self._safe_divide(
                    storage_data['volumes']['used'], storage_data['volumes']['limit'])
                storage_data['gigabytes']['percent'] = self._safe_divide(
                    storage_data['gigabytes']['used'], storage_data['gigabytes']['limit'])
                storage_data['snapshots']['percent'] = self._safe_divide(
                    storage_data['snapshots']['used'], storage_data['snapshots']['limit'])
            except Exception as e:
                LOG.error("Error retrieving storage data: %s", e)
                storage_data = None
            
            # ===== 3. 网络资源 =====
            try:
                neutron_quotas = api.neutron.tenant_quota_get(self.request, tenant_id)
                
                # 获取实际使用数量
                networks = api.neutron.network_list_for_tenant(self.request, tenant_id)
                floatingips = api.neutron.tenant_floating_ip_list(self.request)
                routers = api.neutron.router_list(self.request, tenant_id=tenant_id)
                security_groups = api.neutron.security_group_list(self.request, tenant_id=tenant_id)
                
                network_data = {
                    'networks': {
                        'used': len(networks),
                        'limit': self._normalize_quota(neutron_quotas.get('network', 0)),
                    },
                    'floatingips': {
                        'used': len(floatingips),
                        'limit': self._normalize_quota(neutron_quotas.get('floatingip', 0)),
                    },
                    'routers': {
                        'used': len(routers),
                        'limit': self._normalize_quota(neutron_quotas.get('router', 0)),
                    },
                    'security_groups': {
                        'used': len(security_groups),
                        'limit': self._normalize_quota(neutron_quotas.get('security_group', 0)),
                    },
                }
                network_data['networks']['percent'] = self._safe_divide(
                    network_data['networks']['used'], network_data['networks']['limit'])
                network_data['floatingips']['percent'] = self._safe_divide(
                    network_data['floatingips']['used'], network_data['floatingips']['limit'])
                network_data['routers']['percent'] = self._safe_divide(
                    network_data['routers']['used'], network_data['routers']['limit'])
                network_data['security_groups']['percent'] = self._safe_divide(
                    network_data['security_groups']['used'], network_data['security_groups']['limit'])
            except Exception as e:
                LOG.error("Error retrieving network data: %s", e)
                network_data = None
            
            # ===== 4. 实例详情列表 =====
            try:
                # api.nova.server_list 返回 (servers, has_more_data) 元组
                instances, has_more = api.nova.server_list(self.request)
                instance_details = []
                
                for instance in instances:
                    # 获取实例的 flavor 信息
                    try:
                        flavor = api.nova.flavor_get(self.request, instance.flavor['id'])
                        vcpus = flavor.vcpus
                        ram = flavor.ram
                        disk = flavor.disk
                    except Exception:
                        vcpus = 0
                        ram = 0
                        disk = 0
                    
                    # 计算运行时长
                    try:
                        created_time = getattr(instance, 'created', None)
                        if created_time:
                            if isinstance(created_time, str):
                                created_dt = datetime.strptime(created_time.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                            else:
                                created_dt = created_time
                            uptime = datetime.now() - created_dt.replace(tzinfo=None)
                            uptime_str = f"{uptime.days}天 {uptime.seconds//3600}小时"
                        else:
                            uptime_str = "未知"
                    except Exception:
                        uptime_str = "未知"
                    
                    instance_details.append({
                        'id': instance.id,
                        'name': instance.name,
                        'status': instance.status,
                        'vcpus': vcpus,
                        'ram': ram,  # MB
                        'disk': disk,  # GB
                        'uptime': uptime_str,
                    })
                
            except Exception as e:
                LOG.error("Error retrieving instance details: %s", e)
                instance_details = []
            
            # ===== 5. 资源健康度评分 =====
            health_warnings = []
            if compute_data:
                if compute_data['instances']['percent'] > 80:
                    health_warnings.append(_("实例配额使用超过80%，建议申请扩容"))
                if compute_data['cores']['percent'] > 80:
                    health_warnings.append(_("CPU配额使用超过80%，建议申请扩容"))
                if compute_data['ram']['percent'] > 80:
                    health_warnings.append(_("内存配额使用超过80%，建议申请扩容"))
            
            if storage_data:
                if storage_data['gigabytes']['percent'] > 80:
                    health_warnings.append(_("存储空间使用超过80%，建议清理或扩容"))
            
            if network_data:
                if network_data['floatingips']['percent'] > 80:
                    health_warnings.append(_("浮动IP配额使用超过80%，建议释放未使用的IP"))

            # 保存资源快照到数据库（用于历史趋势分析）
            try:
                snapshot = TenantResourceSnapshot(
                    tenant_id=tenant_id,
                    instances_used=compute_data['instances']['used'],
                    instances_limit=compute_data['instances']['limit'],
                    cores_used=compute_data['cores']['used'],
                    cores_limit=compute_data['cores']['limit'],
                    ram_used=compute_data['ram']['used'],
                    ram_limit=compute_data['ram']['limit'],
                    volumes_used=storage_data['volumes']['used'] if storage_data else 0,
                    volumes_limit=storage_data['volumes']['limit'] if storage_data else 0,
                    gigabytes_used=storage_data['gigabytes']['used'] if storage_data else 0,
                    gigabytes_limit=storage_data['gigabytes']['limit'] if storage_data else 0,
                    snapshots_used=storage_data['snapshots']['used'] if storage_data else 0,
                    snapshots_limit=storage_data['snapshots']['limit'] if storage_data else 0,
                    networks_used=network_data['networks']['used'] if network_data else 0,
                    networks_limit=network_data['networks']['limit'] if network_data else 0,
                    floatingips_used=network_data['floatingips']['used'] if network_data else 0,
                    floatingips_limit=network_data['floatingips']['limit'] if network_data else 0,
                    routers_used=network_data['routers']['used'] if network_data else 0,
                    routers_limit=network_data['routers']['limit'] if network_data else 0,
                    security_groups_used=network_data['security_groups']['used'] if network_data else 0,
                    security_groups_limit=network_data['security_groups']['limit'] if network_data else 0,
                )
                snapshot.save()
                LOG.info("Resource snapshot saved for tenant %s", tenant_id)
            except Exception as e:
                LOG.error("Error saving tenant resource snapshot: %s", e)
                import traceback
                LOG.error("Traceback: %s", traceback.format_exc())

            context.update({
                'compute_data': compute_data,
                'storage_data': storage_data,
                'network_data': network_data,
                'instance_details': instance_details,
                'health_warnings': health_warnings,
                'has_data': True,
            })

            # 获取最近7天的历史数据用于趋势展示
            try:
                seven_days_ago = datetime.now() - timedelta(days=7)
                history_data = TenantResourceSnapshot.objects.filter(
                    tenant_id=tenant_id,
                    created_at__gte=seven_days_ago
                ).order_by('created_at')

                if history_data.exists():
                    # 将数据转换为前端可用的格式
                    trend_data = {
                        'dates': [h.created_at.strftime('%m-%d') for h in history_data],
                        'instances': [h.instances_used for h in history_data],
                        'cores': [h.cores_used for h in history_data],
                        'ram': [h.ram_used for h in history_data],
                        'volumes': [h.volumes_used for h in history_data],
                        'gigabytes': [h.gigabytes_used for h in history_data],
                        'floatingips': [h.floatingips_used for h in history_data],
                    }
                    context['trend_data'] = trend_data
                    context['has_history'] = True
                else:
                    context['has_history'] = False
            except Exception as e:
                LOG.error("Error retrieving history data: %s", e)
                context['has_history'] = False

        except Exception as e:
            LOG.error("Error retrieving comprehensive resource data: %s", e)
            import traceback
            LOG.error("Traceback: %s", traceback.format_exc())
            context['has_data'] = False
            context['error_message'] = _("无法获取资源信息: %s") % str(e)

        return context


class HistoryView(views.HorizonTemplateView):
    """历史资源使用趋势分析视图"""
    template_name = 'custom_reports/comprehensive_overview/history.html'
    page_title = _("资源使用历史趋势")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            tenant_id = self.request.user.tenant_id

            # 获取最近30天的历史数据
            thirty_days_ago = datetime.now() - timedelta(days=30)
            history_data = TenantResourceSnapshot.objects.filter(
                tenant_id=tenant_id,
                created_at__gte=thirty_days_ago
            ).order_by('created_at')

            if history_data.exists():
                # 准备详细的历史数据
                detailed_history = {
                    'dates': [h.created_at.strftime('%Y-%m-%d %H:%M') for h in history_data],
                    'compute': {
                        'instances': [h.instances_used for h in history_data],
                        'instances_limit': [h.instances_limit for h in history_data],
                        'cores': [h.cores_used for h in history_data],
                        'cores_limit': [h.cores_limit for h in history_data],
                        'ram': [h.ram_used for h in history_data],
                        'ram_limit': [h.ram_limit for h in history_data],
                    },
                    'storage': {
                        'volumes': [h.volumes_used for h in history_data],
                        'volumes_limit': [h.volumes_limit for h in history_data],
                        'gigabytes': [h.gigabytes_used for h in history_data],
                        'gigabytes_limit': [h.gigabytes_limit for h in history_data],
                        'snapshots': [h.snapshots_used for h in history_data],
                        'snapshots_limit': [h.snapshots_limit for h in history_data],
                    },
                    'network': {
                        'networks': [h.networks_used for h in history_data],
                        'networks_limit': [h.networks_limit for h in history_data],
                        'floatingips': [h.floatingips_used for h in history_data],
                        'floatingips_limit': [h.floatingips_limit for h in history_data],
                        'routers': [h.routers_used for h in history_data],
                        'routers_limit': [h.routers_limit for h in history_data],
                        'security_groups': [h.security_groups_used for h in history_data],
                        'security_groups_limit': [h.security_groups_limit for h in history_data],
                    }
                }

                # 计算平均值用于分析
                avg_usage = {
                    'compute': {
                        'instances': history_data.aggregate(avg=Avg('instances_used'))['avg'],
                        'cores': history_data.aggregate(avg=Avg('cores_used'))['avg'],
                        'ram': history_data.aggregate(avg=Avg('ram_used'))['avg'],
                    },
                    'storage': {
                        'volumes': history_data.aggregate(avg=Avg('volumes_used'))['avg'],
                        'gigabytes': history_data.aggregate(avg=Avg('gigabytes_used'))['avg'],
                    },
                    'network': {
                        'floatingips': history_data.aggregate(avg=Avg('floatingips_used'))['avg'],
                    }
                }

                context['detailed_history'] = detailed_history
                context['avg_usage'] = avg_usage
                context['has_history'] = True
                context['record_count'] = history_data.count()
            else:
                context['has_history'] = False
                context['record_count'] = 0

        except Exception as e:
            LOG.error("Error retrieving history data: %s", e)
            import traceback
            LOG.error("Traceback: %s", traceback.format_exc())
            context['has_history'] = False
            context['error_message'] = _("无法获取历史数据: %s") % str(e)

        return context

