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

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from openstack_dashboard.dashboards.custom_reports.models import TenantResourceSnapshot


class Command(BaseCommand):
    help = '清理旧的资源快照数据（默认保留30天）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='保留最近N天的数据（默认30天）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='模拟运行，不实际删除数据',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # 计算截止日期
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # 查询要删除的记录
        old_snapshots = TenantResourceSnapshot.objects.filter(
            created_at__lt=cutoff_date
        )
        
        count = old_snapshots.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[模拟运行] 将删除 {count} 条早于 {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")} 的记录'
                )
            )
            
            # 显示按租户统计的记录数
            from django.db.models import Count
            tenant_counts = old_snapshots.values('tenant_id').annotate(
                count=Count('id')
            ).order_by('-count')
            
            self.stdout.write('\n按租户统计将删除的记录数：')
            for item in tenant_counts[:10]:  # 只显示前10个
                self.stdout.write(
                    f"  租户 {item['tenant_id']}: {item['count']} 条记录"
                )
            
            if tenant_counts.count() > 10:
                self.stdout.write(f"  ... 还有 {tenant_counts.count() - 10} 个租户")
        else:
            # 实际删除
            self.stdout.write(
                self.style.WARNING(
                    f'正在删除 {count} 条早于 {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")} 的记录...'
                )
            )
            
            deleted_count, _ = old_snapshots.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功删除 {deleted_count} 条记录'
                )
            )
        
        # 显示当前数据库状态
        total_count = TenantResourceSnapshot.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\n当前数据库中共有 {total_count} 条快照记录'
            )
        )
        
        if total_count > 0:
            oldest = TenantResourceSnapshot.objects.order_by('created_at').first()
            newest = TenantResourceSnapshot.objects.order_by('-created_at').first()
            self.stdout.write(
                f'最早记录：{oldest.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
            )
            self.stdout.write(
                f'最新记录：{newest.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
            )

