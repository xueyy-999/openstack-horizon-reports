# OpenStack Horizon 自定义报表系统 - 部署文档

## 📋 环境要求

- Ubuntu 20.04/22.04 或 CentOS 8+
- OpenStack DevStack（已安装）
- Python 3.8+
- MySQL 5.7+ / 8.0+

---

## 🚀 快速部署（10分钟）

### 步骤 1：创建数据库

```bash
# 连接 MySQL
mysql -uroot -psecret -h127.0.0.1

# 创建数据库
CREATE DATABASE horizon_custom DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 步骤 2：传输项目文件

```bash
# 假设项目在本地，传输到 DevStack 服务器
# 替换 <your-project-path> 为实际路径
# 替换 <devstack-host> 为 DevStack 服务器 IP
# 传过去的目录及文件要全部把属主属组改为stack用户！！！！！！！！！！！

cd <your-project-path>

# 传输 Dashboard 目录
scp -r openstack_dashboard/dashboards/custom_reports \
    stack@<devstack-host>:/opt/stack/horizon/openstack_dashboard/dashboards/

# 传输启用配置
scp openstack_dashboard/enabled/_60_custom_reports.py \
    stack@<devstack-host>:/opt/stack/horizon/openstack_dashboard/enabled/

# 传输数据库配置
scp openstack_dashboard/local/local_settings.py \
    stack@<devstack-host>:/opt/stack/horizon/openstack_dashboard/local/
```

### 步骤 3：执行数据库迁移

```bash
# SSH 登录到 DevStack 服务器
ssh stack@<devstack-host>

# 激活虚拟环境
source /opt/stack/data/venv/bin/activate

# 进入 Horizon 目录
cd /opt/stack/horizon

# 生成迁移文件
python manage.py makemigrations custom_reports

# 执行迁移
python manage.py migrate

# 验证表创建
mysql -uroot -psecret -h127.0.0.1 -e "USE horizon_custom; SHOW TABLES;"
```

**预期输出**：
```
+-----------------------------+
| Tables_in_horizon_custom    |
+-----------------------------+
| tenant_resource_snapshot    |
+-----------------------------+
```

### 步骤 4：收集静态文件

```bash
# 确保在虚拟环境中
cd /opt/stack/horizon

# 收集静态文件
python manage.py collectstatic --noinput  --clear

# 压缩静态文件（生产环境）
python manage.py compress --force

# 验证静态文件
ls -la static/custom_reports/css/reports.css
ls -la static/custom_reports/js/charts.js
```

### 步骤 5：重启 Apache

```bash
# 重启 Apache
sudo systemctl restart apache2

# 检查状态
sudo systemctl status apache2

# 查看日志（确保无错误）
sudo tail -n 50 /var/log/apache2/error.log | grep -i error
```

### 步骤 6：访问系统

```bash
# 浏览器访问
http://<devstack-host>/dashboard/

# 登录账号（DevStack 默认）
用户名: admin
密码: secret
域: default
```

---

## ✅ 验证步骤

### 验证 1：代码结构（4.1）

```bash
# 检查目录结构
cd /opt/stack/horizon
tree -L 3 openstack_dashboard/dashboards/custom_reports/

# 检查关键文件
ls -la openstack_dashboard/dashboards/custom_reports/dashboard.py
ls -la openstack_dashboard/dashboards/custom_reports/models.py
ls -la openstack_dashboard/dashboards/custom_reports/comprehensive_overview/views.py
ls -la openstack_dashboard/dashboards/custom_reports/resource_usage/views.py
ls -la openstack_dashboard/enabled/_60_custom_reports.py

# 检查数据库配置
grep -A 10 "DATABASES" openstack_dashboard/local/local_settings.py
```

**预期结果**：
- ✓ 所有目录存在
- ✓ 关键文件存在
- ✓ 数据库配置正确

---

### 验证 2：功能验证（4.2）

#### 2.1 Dashboard 显示测试

```bash
# 操作步骤
1. 登录 Horizon Dashboard
2. 查看左侧导航栏

# 检查点
✓ 显示"自定义报表"菜单项
✓ 点击展开显示两个子菜单：
  - 综合资源概览
  - 资源使用情况
✓ 点击可以正常跳转
```

#### 2.2 综合资源概览测试

```bash
# 访问页面
URL: http://<devstack-host>/dashboard/custom_reports/comprehensive_overview/

# 检查显示内容
✓ 计算资源卡片
  - 实例数量（已用/配额）
  - CPU 核心（已用/配额）
  - 内存 MB（已用/配额）
  - 进度条显示使用率

✓ 存储资源卡片
  - 卷数量（已用/配额）
  - 存储空间 GB（已用/配额）
  - 快照数量（已用/配额）

✓ 网络资源卡片
  - 网络数量（已用/配额）
  - 浮动 IP（已用/配额）
  - 路由器（已用/配额）
  - 安全组（已用/配额）

✓ 实例资源占用详情表
  - 实例名称
  - 状态
  - CPU 核心
  - 内存 (MB)
  - 磁盘 (GB)
  - 运行时长

✓ 资源配额使用率对比图（柱状图）
✓ 资源分类占用图（环形图）
```

**数据验证命令**：
```bash
# 对比实例数量
openstack server list
nova list

# 对比卷数量
openstack volume list
cinder list

# 对比网络数量
openstack network list
neutron net-list

# 对比配额
openstack quota show
```

#### 2.3 资源使用情况测试

```bash
# 访问页面
URL: http://<devstack-host>/dashboard/custom_reports/resource_usage/

# 检查显示内容
✓ 计算实例卡片
  - 实例使用进度条
  - 已用/配额数值

✓ CPU 核心卡片
  - CPU 使用进度条
  - 已用/配额数值

✓ 内存卡片
  - 内存使用进度条
  - 已用/配额数值（MB）

✓ 资源使用分布图（环形图）
  - Chart.js 图表正常加载
  - 数据显示准确
```

#### 2.4 历史数据功能测试

```bash
# 多次访问综合资源概览页面（至少 3 次）
# 然后检查数据库

# 查询数据库
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SELECT 
    tenant_id,
    created_at,
    instances_used,
    cores_used,
    ram_used
FROM tenant_resource_snapshot
ORDER BY created_at DESC
LIMIT 10;
"

# 检查数据条数
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SELECT COUNT(*) as total_snapshots FROM tenant_resource_snapshot;
"
```

**预期结果**：
- ✓ 每次访问页面都会新增一条记录
- ✓ 记录包含完整的资源信息
- ✓ 时间戳正确

#### 2.5 历史趋势图测试

```bash
# 访问历史分析页面
URL: http://<devstack-host>/dashboard/custom_reports/comprehensive_overview/history/

# 检查显示内容
✓ 最近 30 天的详细历史数据
✓ 计算资源趋势图（实例、CPU、内存）
✓ 存储资源趋势图（卷、空间、快照）
✓ 网络资源趋势图
✓ 平均使用率统计
```

---

### 验证 3：部署验证（4.3）

#### 3.1 数据库迁移验证

```bash
# 检查迁移文件
ls -la /opt/stack/horizon/openstack_dashboard/dashboards/custom_reports/migrations/

# 查看表结构
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
DESCRIBE tenant_resource_snapshot;
"
```

**预期输出**：
```
+----------------------+--------------+------+-----+---------+----------------+
| Field                | Type         | Null | Key | Default | Extra          |
+----------------------+--------------+------+-----+---------+----------------+
| id                   | bigint       | NO   | PRI | NULL    | auto_increment |
| tenant_id            | varchar(64)  | NO   | MUL | NULL    |                |
| created_at           | datetime(6)  | NO   |     | NULL    |                |
| instances_used       | int          | NO   |     | NULL    |                |
| instances_limit      | int          | NO   |     | NULL    |                |
| cores_used           | int          | NO   |     | NULL    |                |
| cores_limit          | int          | NO   |     | NULL    |                |
| ram_used             | int          | NO   |     | NULL    |                |
| ram_limit            | int          | NO   |     | NULL    |                |
| volumes_used         | int          | NO   |     | NULL    |                |
| volumes_limit        | int          | NO   |     | NULL    |                |
| gigabytes_used       | int          | NO   |     | NULL    |                |
| gigabytes_limit      | int          | NO   |     | NULL    |                |
| snapshots_used       | int          | NO   |     | NULL    |                |
| snapshots_limit      | int          | NO   |     | NULL    |                |
| networks_used        | int          | NO   |     | NULL    |                |
| networks_limit       | int          | NO   |     | NULL    |                |
| floatingips_used     | int          | NO   |     | NULL    |                |
| floatingips_limit    | int          | NO   |     | NULL    |                |
| routers_used         | int          | NO   |     | NULL    |                |
| routers_limit        | int          | NO   |     | NULL    |                |
| security_groups_used | int          | NO   |     | NULL    |                |
| security_groups_limit| int          | NO   |     | NULL    |                |
+----------------------+--------------+------+-----+---------+----------------+
```

**检查索引**：
```bash
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SHOW INDEX FROM tenant_resource_snapshot;
"
```

**预期结果**：
- ✓ 主键索引（id）
- ✓ tenant_id 索引

---

#### 3.2 静态文件验证

```bash
# 检查 CSS 文件
cat /opt/stack/horizon/static/custom_reports/css/reports.css | head -20

# 检查 JS 文件
cat /opt/stack/horizon/static/custom_reports/js/charts.js | head -20

# 检查文件权限
ls -la /opt/stack/horizon/static/custom_reports/

# 检查文件大小
du -sh /opt/stack/horizon/static/custom_reports/
```

**预期结果**：
- ✓ CSS 文件存在且内容正确
- ✓ JS 文件存在且内容正确
- ✓ 文件权限正确（www-data 可读）

---

#### 3.3 服务运行验证

```bash
# 检查 Apache 状态
sudo systemctl status apache2

# 检查 Apache 配置
sudo apache2ctl configtest

# 检查进程
ps aux | grep apache2

# 检查端口监听
sudo netstat -tulnp | grep :80

# 检查错误日志
sudo tail -n 100 /var/log/apache2/error.log | grep -i "custom_reports"

# 检查访问日志
sudo tail -n 50 /var/log/apache2/access.log | grep "custom_reports"
```

**预期结果**：
- ✓ Apache 状态：active (running)
- ✓ 配置测试：Syntax OK
- ✓ 端口 80/443 正常监听
- ✓ 无错误日志

---

#### 3.4 功能完整性测试

```bash
# 创建测试实例
openstack server create \
    --flavor m1.tiny \
    --image cirros-0.5.2-x86_64-disk \
    --network private \
    test-vm-001

# 等待实例创建完成
openstack server list

# 刷新报表页面，验证以下内容
1. 实例数量从 N 增加到 N+1
2. CPU 核心数增加（根据 flavor）
3. 内存使用量增加
4. 实例详情表中显示新实例
5. 数据库新增一条快照记录

# 验证数据库
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SELECT 
    created_at,
    instances_used,
    cores_used,
    ram_used
FROM tenant_resource_snapshot
ORDER BY created_at DESC
LIMIT 5;
"

# 删除测试实例
openstack server delete test-vm-001
```

**预期结果**：
- ✓ 页面数据实时更新
- ✓ 图表动态刷新
- ✓ 数据库自动保存新快照
- ✓ 实例详情表显示正确

---

## 🧪 完整测试流程

### 测试场景 1：首次访问

```bash
# 1. 清空数据库（可选）
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
TRUNCATE TABLE tenant_resource_snapshot;
"

# 2. 访问综合资源概览页面
# 浏览器访问：http://<devstack-host>/dashboard/custom_reports/comprehensive_overview/

# 3. 检查数据库
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SELECT COUNT(*) as count FROM tenant_resource_snapshot;
"

# 预期：count = 1
```

---

### 测试场景 2：历史趋势

```bash
# 1. 多次访问页面（间隔 1 分钟，至少 5 次）
for i in {1..5}; do
    echo "访问第 $i 次..."
    curl -s http://localhost/dashboard/custom_reports/comprehensive_overview/ \
         -H "Cookie: sessionid=<your-session-id>" > /dev/null
    sleep 60
done

# 2. 查看数据库
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SELECT 
    created_at,
    instances_used,
    cores_used
FROM tenant_resource_snapshot
ORDER BY created_at DESC;
"

# 3. 访问历史页面
# http://<devstack-host>/dashboard/custom_reports/comprehensive_overview/history/

# 预期：显示趋势图
```

---

### 测试场景 3：资源变化监控

```bash
# 1. 记录当前资源
openstack server list
openstack volume list

# 2. 创建新资源
openstack server create --flavor m1.small --image cirros test-vm-monitor
openstack volume create --size 10 test-volume-monitor

# 3. 刷新报表页面

# 4. 验证变化
# 检查点：
# - 实例数量 +1
# - CPU 核心数增加
# - 内存使用增加
# - 卷数量 +1
# - 存储空间 +10GB

# 5. 清理资源
openstack server delete test-vm-monitor
openstack volume delete test-volume-monitor
```

---

## 🔧 数据清理（可选）

### 手动清理历史数据

```bash
# 清理 30 天前的数据
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
DELETE FROM tenant_resource_snapshot 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
"

# 查看剩余数据量
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SELECT COUNT(*) as remaining FROM tenant_resource_snapshot;
"
```

### 使用管理命令清理

```bash
# 激活虚拟环境
source /opt/stack/data/venv/bin/activate
cd /opt/stack/horizon

# 模拟运行（不实际删除）
python manage.py cleanup_old_snapshots --days=30 --dry-run

# 实际清理
python manage.py cleanup_old_snapshots --days=30

# 查看帮助
python manage.py cleanup_old_snapshots --help
```

---

## 🐛 故障排查

### 问题 1：Dashboard 不显示

```bash
# 检查配置文件
cat /opt/stack/horizon/openstack_dashboard/enabled/_60_custom_reports.py

# 确认 DISABLED = False
# 检查语法错误
python -m py_compile /opt/stack/horizon/openstack_dashboard/enabled/_60_custom_reports.py

# 重启 Apache
sudo systemctl restart apache2
```

---

### 问题 2：实例详情不显示

```bash
# 检查日志
sudo tail -f /var/log/apache2/error.log | grep custom_reports

# 检查是否有实例
openstack server list

# 检查代码（关键行）
grep "instances, has_more" /opt/stack/horizon/openstack_dashboard/dashboards/custom_reports/comprehensive_overview/views.py

# 应该看到：
# instances, has_more = api.nova.server_list(self.request)
```

---

### 问题 3：数据库连接失败

```bash
# 测试数据库连接
mysql -uroot -psecret -h127.0.0.1 -e "SHOW DATABASES;"

# 检查配置
grep -A 10 "DATABASES" /opt/stack/horizon/openstack_dashboard/local/local_settings.py

# 检查 MySQL 服务
sudo systemctl status mysql

# 检查权限
mysql -uroot -psecret -h127.0.0.1 -e "
SHOW GRANTS FOR 'root'@'localhost';
"
```

---

### 问题 4：图表不显示

```bash
# 检查浏览器控制台（F12）
# 查看是否有 JavaScript 错误

# 检查 Chart.js 加载
curl -I https://cdn.jsdelivr.net/npm/chart.js

# 如果 CDN 无法访问，下载本地版本
cd /opt/stack/horizon/openstack_dashboard/dashboards/custom_reports/static/custom_reports/js/
wget https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js

# 修改模板引用为本地文件
```

---

### 问题 5：静态文件 404

```bash
# 重新收集静态文件
cd /opt/stack/horizon
python manage.py collectstatic --noinput --clear

# 检查 Apache 配置
cat /etc/apache2/sites-available/horizon.conf | grep Alias

# 检查权限
ls -la /opt/stack/horizon/static/custom_reports/

# 修复权限
sudo chown -R www-data:www-data /opt/stack/horizon/static/
```

---

## 📊 性能优化建议

### 数据库优化

```bash
# 添加索引（如果还没有）
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
CREATE INDEX idx_created_at ON tenant_resource_snapshot(created_at);
CREATE INDEX idx_tenant_created ON tenant_resource_snapshot(tenant_id, created_at);
"

# 查看索引使用情况
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
EXPLAIN SELECT * FROM tenant_resource_snapshot 
WHERE tenant_id = 'xxx' 
ORDER BY created_at DESC LIMIT 10;
"
```

### 定期清理任务

```bash
# 添加 cron 任务
crontab -e

# 添加以下内容（每天凌晨 2 点清理 30 天前的数据）
0 2 * * * cd /opt/stack/horizon && source /opt/stack/data/venv/bin/activate && python manage.py cleanup_old_snapshots --days=30 >> /var/log/horizon/cleanup.log 2>&1
```

---

## ✅ 验证清单

**代码结构验证**：
- [ ] 目录结构完整
- [ ] 所有 Python 文件存在
- [ ] 配置文件正确
- [ ] 无语法错误

**功能验证**：
- [ ] Dashboard 菜单显示
- [ ] 综合资源概览显示正确
- [ ] 资源使用情况显示正确
- [ ] 实例详情表显示
- [ ] 图表正常加载
- [ ] 数据库自动保存快照
- [ ] 历史趋势图显示

**部署验证**：
- [ ] 数据库迁移成功
- [ ] 数据表结构正确
- [ ] 静态文件收集完成
- [ ] Apache 正常运行
- [ ] 无错误日志
- [ ] 页面可以访问

**性能验证**：
- [ ] 页面加载 < 3 秒
- [ ] 数据库查询使用索引
- [ ] 无慢查询

---

## 📝 快速命令参考

```bash
# 环境激活
source /opt/stack/data/venv/bin/activate
cd /opt/stack/horizon

# 数据库操作
mysql -uroot -psecret -h127.0.0.1 -e "USE horizon_custom; SELECT COUNT(*) FROM tenant_resource_snapshot;"

# 静态文件
python manage.py collectstatic --noinput

# 重启服务
sudo systemctl restart apache2

# 查看日志
sudo tail -f /var/log/apache2/error.log

# 清理数据
python manage.py cleanup_old_snapshots --days=30

# 检查实例
openstack server list

# 检查配额
openstack quota show
```

---

**部署完成！访问 `http://<your-host>/dashboard/` 查看效果。** 🎉

