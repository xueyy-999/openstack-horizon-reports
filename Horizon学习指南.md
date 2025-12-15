# OpenStack Horizon 完整学习指南

## 项目概述

Horizon 是 OpenStack 的官方 Web 仪表板，基于 Django 框架构建。它为 OpenStack 云平台提供了一个完整的 Web 界面，允许用户通过浏览器管理和操作 OpenStack 的各种服务。

注：本文以 Linux DevStack 环境为基准进行说明。

### 核心特性
- **Django 框架**：基于 Python Django Web 框架
- **模块化设计**：可扩展的插件架构
- **多服务集成**：集成 Nova、Neutron、Cinder、Glance、Keystone 等服务
- **主题支持**：支持自定义主题和品牌
- **国际化**：支持多语言界面

## 项目结构详解（基于实际项目文件）

### 根目录结构
```
./                          # 项目根目录
├── horizon/               # 核心框架代码
├── openstack_dashboard/   # 主要应用代码
├── openstack_auth/        # 认证模块
├── static/               # 静态文件
├── doc/                  # 文档
├── tools/                # 开发工具
├── manage.py             # Django 管理脚本
├── requirements.txt      # Python 依赖
├── package.json          # 前端依赖
├── tox.ini              # 测试配置
├── setup.py             # 安装配置
├── setup.cfg            # 项目元数据
└── README.rst           # 项目说明
```

### 核心目录详解

#### 1. horizon/ - 核心框架（实际文件结构）
```
horizon/
├── __init__.py           # 包初始化
├── base.py              # 基础类定义（Dashboard、Panel 基类）
├── views.py             # 基础视图
├── defaults.py          # 默认配置
├── exceptions.py        # 异常处理
├── forms/               # 表单组件
├── tables/              # 表格组件
├── tabs/                # 标签页组件
├── workflows/           # 工作流组件
├── templates/           # 模板文件
├── static/              # 静态资源
├── utils/               # 工具函数
├── middleware/          # 中间件
├── browsers/            # 浏览器相关
├── contrib/             # 贡献组件
└── test/               # 测试文件
```

**核心组件说明（基于 horizon/base.py）：**
- **Dashboard**: 仪表板基类，定义导航结构
- **Panel**: 面板基类，实现具体功能页面
- **Table**: 数据表格组件，支持排序、分页、操作
- **Form**: 表单组件，处理用户输入
- **Workflow**: 多步骤操作流程
- **Tab**: 标签页组织内容

#### 2. openstack_dashboard/ - 主应用（实际文件结构）
```
openstack_dashboard/
├── __init__.py
├── settings.py          # Django 配置
├── defaults.py          # 默认配置
├── urls.py             # URL 路由
├── wsgi.py             # WSGI 入口
├── api/                # OpenStack API 封装
├── dashboards/         # 各功能模块
│   ├── admin/          # 管理员功能
│   ├── project/        # 项目功能
│   ├── identity/       # 身份管理
│   ├── settings/       # 设置
│   └── custom_reports/ # 自定义报告
├── templates/          # 模板文件
├── static/            # 静态文件
├── enabled/           # 功能开关配置
├── local/             # 本地配置
├── themes/            # 主题文件
├── utils/             # 工具函数
└── test/              # 测试文件
```

#### 3. API 层结构（openstack_dashboard/api/ 实际文件）
```
openstack_dashboard/api/
├── __init__.py
├── base.py             # API 基础类
├── nova.py             # 计算服务 API
├── _nova.py            # Nova 内部实现
├── neutron.py          # 网络服务 API
├── network.py          # 网络 API
├── cinder.py           # 存储服务 API
├── glance.py           # 镜像服务 API
├── keystone.py         # 身份服务 API
├── swift.py            # 对象存储 API
├── placement.py        # 资源调度 API
├── microversions.py    # 微版本管理
└── rest/              # REST API 接口
```

## 实际项目文件分析

### 1. 关键配置文件详解

#### manage.py（项目根目录）
```python
#!/usr/bin/env python3
# 实际的 Django 管理脚本
import os
import sys
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openstack_dashboard.settings")
    execute_from_command_line(sys.argv)
```

#### requirements.txt（实际依赖）
项目根目录的 `requirements.txt` 包含了所有 Python 依赖，包括：
- Django 4.2
- OpenStack 客户端库（novaclient、neutronclient 等）
- XStatic 前端库
- 其他工具库

#### package.json（前端配置）
```json
{
  "name": "horizon",
  "description": "OpenStack Horizon - Angular",
  "devDependencies": {
    "eslint": "3.0.0",
    "karma": "5.2.3",
    "jasmine-core": "3.6.0"
  },
  "scripts": {
    "test": "karma start horizon/karma.conf.js --single-run && karma start openstack_dashboard/karma.conf.js --single-run",
    "lint": "eslint --no-color openstack_dashboard/static horizon/static openstack_dashboard/dashboards/*/static"
  }
}
```

### 2. 启动和运行

#### 重要：DevStack 的 Python 虚拟环境

**DevStack 使用虚拟环境运行 Horizon**

DevStack 会创建并使用 Python 虚拟环境，通常位于：`/opt/stack/data/venv`

**验证虚拟环境：**
```bash
# 1. 查看 Apache 配置确认虚拟环境路径
sudo cat /etc/apache2/sites-available/horizon.conf | grep WSGIPythonHome
# 输出：WSGIPythonHome /opt/stack/data/venv
# 注意：WSGIPythonHome 在 </VirtualHost> 标签之外（全局配置）

# 2. 查看完整的 WSGI 配置
sudo cat /etc/apache2/sites-available/horizon.conf | grep -E "WSGI|python"
# 可以看到 WSGIDaemonProcess、WSGIProcessGroup 等配置

# 3. 查看 manage.py 的 Python 解释器
head -n 1 /opt/stack/horizon/manage.py
# 输出：#!/usr/bin/env python3

# 4. 查看虚拟环境结构
ls -la /opt/stack/data/venv/
# 应该看到：bin/ lib/ include/ pyvenv.cfg

# 5. 查看虚拟环境的 Python 版本
/opt/stack/data/venv/bin/python3 --version

# 6. 查看虚拟环境中安装的包
/opt/stack/data/venv/bin/pip3 list | grep -E "django|horizon|openstack"

# 7. 验证 Apache 是否使用正确的 Python
# 方法1：检查加载的模块
sudo apache2ctl -M | grep wsgi
# 输出：wsgi_module (shared)

# 方法2：查看运行中的进程
ps aux | grep "WSGIDaemonProcess horizon" | grep -v grep
```

#### 开发环境启动

**在 DevStack 环境中（推荐）：**

```bash
# 1. 激活虚拟环境（重要！）
source /opt/stack/data/venv/bin/activate
# 提示符会变为：(venv) stack@ubuntu:~$

# 2. 验证当前使用的 Python
which python3
# 应该输出：/opt/stack/data/venv/bin/python3

# 3. 进入 Horizon 目录
cd /opt/stack/horizon

# 4. 加载 OpenStack 环境变量
source /opt/stack/devstack/openrc admin admin

# 5. 启动开发服务器
python3 manage.py runserver 0.0.0.0:8000

# 访问：http://<your-ip>:8000
```

**独立开发环境（非 DevStack）：**

```bash
# 1. 创建虚拟环境（如果还没有）
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
pip install -r test-requirements.txt

# 4. 前端依赖
npm install

# 5. 数据库迁移（如需要）
python manage.py migrate

# 6. 收集静态文件
python manage.py collectstatic --noinput

# 7. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

**快速启动脚本（DevStack 环境）：**

创建 `~/start_horizon_dev.sh`：
```bash
#!/bin/bash
set -e

echo "=== Horizon 开发服务器启动 ==="

# 1. 激活虚拟环境
echo "激活虚拟环境..."
source /opt/stack/data/venv/bin/activate

# 2. 显示 Python 信息
echo -e "\nPython 信息:"
echo "  版本: $(python3 --version)"
echo "  路径: $(which python3)"

# 3. 验证关键包
echo -e "\n检查关键包:"
python3 -c "import django; print(f'  Django: {django.get_version()}')"
python3 -c "import horizon; print('  Horizon: OK')"
python3 -c "import openstack_dashboard; print('  OpenStack Dashboard: OK')"

# 4. 加载 OpenStack 环境变量
echo -e "\n加载 OpenStack 环境变量..."
source /opt/stack/devstack/openrc admin admin

# 5. 进入 horizon 目录
cd /opt/stack/horizon

# 6. 启动开发服务器
echo -e "\n启动 Django 开发服务器..."
echo "访问地址: http://$(hostname -I | awk '{print $1}'):8000"
echo "按 Ctrl+C 停止服务器"
echo "================================"
python3 manage.py runserver 0.0.0.0:8000
```

使用方法：
```bash
chmod +x ~/start_horizon_dev.sh
~/start_horizon_dev.sh
```

#### 使用 tox 运行（推荐）
不同分支/版本的环境名称可能不同，请先查看实际可用环境后再执行。
```bash
# 列出可用环境
tox -l

# 运行（以实际环境名为准）
tox -e <env-name-from-tox-l>

# 示例：运行测试/代码检查（名称以 tox -l 输出为准）
tox -e py          # 或 py3x-django4x 等
tox -e pep8        # 或 flake8
```

#### WSGI 部署
```python
# openstack_dashboard/wsgi.py 实际文件用于生产部署
```

### 3. 常用管理命令（基于 tox.ini，环境名称以 `tox -l` 为准）
```bash
# 提取翻译字符串
python manage.py extract_messages

# 编译翻译文件
python manage.py compilemessages

# 运行所有测试（示例，具体以 tox -l 输出为准）
tox -e py     # 或 py3、py311-django42 等

# 代码风格检查（示例）
tox -e pep8   # 或 flake8

# 前端测试（需 package.json 定义 test 脚本）
npm test

# 安全扫描（如有）
tox -e bandit

# 文档构建（如有）
tox -e docs
```

## 实际 Dashboard 和 Panel 结构分析

### 1. Project Dashboard 完整结构
```
openstack_dashboard/dashboards/project/
├── __init__.py
├── dashboard.py                    # Dashboard 定义
├── api_access/                    # API 访问面板
├── backups/                       # 备份管理
├── containers/                    # 容器管理
├── floating_ips/                  # 浮动 IP
├── images/                        # 镜像管理
├── instances/                     # 实例管理
│   ├── __init__.py
│   ├── panel.py                  # Panel 定义
│   ├── views.py                  # 视图实现
│   ├── tables.py                 # 表格定义
│   ├── forms.py                  # 表单定义
│   ├── workflows.py              # 工作流
│   ├── urls.py                   # URL 路由
│   └── templates/                # 模板文件
├── key_pairs/                     # 密钥对管理
├── networks/                      # 网络管理
├── overview/                      # 概览面板
├── routers/                       # 路由器管理
├── security_groups/               # 安全组
├── volumes/                       # 卷管理
└── static/                        # 静态文件
```

### 2. Admin Dashboard 结构
```
openstack_dashboard/dashboards/admin/
├── __init__.py
├── dashboard.py                   # 管理员 Dashboard
├── aggregates/                    # 主机聚合
├── flavors/                       # 规格管理
├── hypervisors/                   # 虚拟机管理程序
├── images/                        # 镜像管理（管理员视图）
├── info/                          # 系统信息
├── instances/                     # 实例管理（管理员视图）
├── networks/                      # 网络管理（管理员视图）
├── overview/                      # 管理员概览
├── routers/                       # 路由器管理（管理员视图）
├── volumes/                       # 卷管理（管理员视图）
└── static/                        # 静态文件
```

### 3. Identity Dashboard 结构
```
openstack_dashboard/dashboards/identity/
├── __init__.py
├── dashboard.py                   # 身份管理 Dashboard
├── domains/                       # 域管理
├── groups/                        # 组管理
├── projects/                      # 项目管理
├── roles/                         # 角色管理
├── users/                         # 用户管理
└── static/                        # 静态文件
```

## 核心概念和架构

### 1. MVC 架构模式

#### Model (模型层)
- **API 客户端**: 通过 Python 客户端库与 OpenStack 服务通信
- **数据封装**: 将 API 响应封装为 Python 对象
- **缓存机制**: 使用 Django 缓存框架提高性能

#### View (视图层)
```python
# 示例：实例列表视图
class IndexView(tables.DataTableView):
    table_class = InstancesTable
    template_name = 'project/instances/index.html'
    
    def get_data(self):
        try:
            instances = api.nova.server_list(self.request)
            return instances
        except Exception:
            exceptions.handle(self.request, _('Unable to retrieve instances.'))
            return []
```

#### Controller (控制器层)
- **URL 路由**: Django URLconf 定义 URL 模式
- **视图函数**: 处理 HTTP 请求和响应
- **中间件**: 处理认证、权限、异常等

### 2. 组件系统（基于实际代码）

#### Dashboard 和 Panel 核心概念详解

**概念理解：**

- **Dashboard（仪表板）**：顶层功能容器，用于按业务领域或功能类别组织相关功能模块
  - 类似于书籍的"章"（Chapter）
  - 继承自 `horizon.Dashboard` 基类（定义在 `horizon/base.py`）
  - 可以包含多个 Panel
  - 具有独立的 slug 标识符和 URL 路径
  - 支持权限控制（policy_rules）
  - 示例：Project（项目管理）、Admin（系统管理）、Identity（身份管理）

- **Panel（面板）**：Dashboard 内的具体功能模块，每个 Panel 对应一个独立的功能页面
  - 类似于书籍的"节"（Section）
  - 继承自 `horizon.Panel` 基类（定义在 `horizon/base.py`）
  - 必须注册到某个 Dashboard
  - 包含独立的视图（views.py）、URL 配置（urls.py）、模板（templates/）
  - 示例：Instances（实例管理）、Volumes（卷管理）、Networks（网络管理）

**层级关系：**
```
Horizon (Site)
    └── Dashboard (例如: Project)
            └── PanelGroup (可选分组)
                    └── Panel (例如: Instances)
                            └── Views (具体的视图和业务逻辑)
```

**URL 结构：**
```
访问路径格式：/horizon/{dashboard_slug}/{panel_slug}/
示例：/horizon/project/instances/
     /horizon/admin/flavors/
     /horizon/custom_reports/resource_usage/
```

**Dashboard 关键属性（基于 horizon/base.py）：**
```python
class Dashboard(Registry, HorizonComponent):
    name = ''                    # 显示名称
    slug = ''                    # 唯一标识符，用于 URL
    panels = []                  # 包含的 Panel 列表（模块名）
    default_panel = None         # 默认显示的 Panel
    permissions = []             # 权限要求
    policy_rules = tuple()       # 策略规则
    nav = True                   # 是否在导航中显示
    public = False               # 是否允许未登录访问
```

**Panel 关键属性（基于 horizon/base.py）：**
```python
class Panel(HorizonComponent):
    name = ''                    # 显示名称
    slug = ''                    # 唯一标识符，用于 URL
    urls = None                  # URL 配置文件路径
    nav = True                   # 是否在导航中显示
    index_url_name = "index"     # 默认视图的 URL name
    permissions = []             # 权限要求
    policy_rules = tuple()       # 策略规则
```

**Project Dashboard 定义（openstack_dashboard/dashboards/project/dashboard.py）：**
```python
from django.utils.translation import gettext_lazy as _
import horizon

class Project(horizon.Dashboard):
    name = _("Project")
    slug = "project"
    panels = ('overview', 'instances', 'volumes', 'images', 'networks')
    default_panel = 'overview'

    def can_access(self, context):
        request = context['request']
        has_project = request.user.token.project.get('id') is not None
        return super().can_access(context) and has_project

horizon.register(Project)
```

**Instances Panel 定义（openstack_dashboard/dashboards/project/instances/panel.py）：**
```python
from django.utils.translation import gettext_lazy as _
import horizon
from openstack_dashboard.dashboards.project import dashboard

class Instances(horizon.Panel):
    name = _("Instances")
    slug = 'instances'
    permissions = ('openstack.services.compute',)

# 注册 Panel 到 Dashboard
dashboard.Project.register(Instances)
```

**注册机制：**
```python
# 1. 创建并注册 Dashboard
class MyDashboard(horizon.Dashboard):
    name = _("My Dashboard")
    slug = "my_dashboard"
    panels = ('my_panel',)
    default_panel = 'my_panel'

horizon.register(MyDashboard)

# 2. 创建并注册 Panel
class MyPanel(horizon.Panel):
    name = _("My Panel")
    slug = "my_panel"

MyDashboard.register(MyPanel)
```

#### 表格组件
```python
class InstancesTable(tables.DataTable):
    name = tables.Column("name", link="horizon:project:instances:detail")
    status = tables.Column("status", status=True)
    
    class Meta:
        name = "instances"
        verbose_name = _("Instances")
        table_actions = (LaunchLink, DeleteInstance)
        row_actions = (EditInstance, DeleteInstance)
```

### 3. 认证和权限

#### 认证流程
1. **用户登录**: 通过 Keystone 验证用户凭据
2. **Token 获取**: 获取认证 Token 和服务目录
3. **会话管理**: 将 Token 存储在 Django 会话中
4. **API 调用**: 使用 Token 调用 OpenStack API

#### 权限控制
```python
# 基于角色的权限检查
@require_auth
def view_function(request):
    if not request.user.has_perm('openstack.services.compute'):
        raise PermissionDenied
```

### 4. Policy 与访问控制（实战）
- Policy 定义：各服务（nova/neutron/cinder/keystone）拥有各自的 policy 文件；Horizon 会根据策略判断操作是否可见/可用。
- 常见排错：
  - 403 禁止：检查对应服务的 policy 条目是否允许当前用户/项目角色。
  - 按钮不可见：Panel/Action 上的 `permissions` 与策略共同决定可见性。
- 参考位置：
  - 面板权限：如 `permissions = ('openstack.services.compute',)`
  - 服务策略：部署端 `/etc/<service>/policy.yaml`（DevStack 环境）。

## API 调用机制（基于实际代码）

### 1. 服务发现和连接机制

**核心机制：通过 Keystone Service Catalog 动态发现服务端点**

Horizon 不需要在代码中硬编码各个 OpenStack 服务的 IP 地址和端口。它采用基于 Keystone Service Catalog（服务目录）的动态服务发现机制。

#### 工作流程

```
用户登录 Horizon
    ↓
通过 OPENSTACK_KEYSTONE_URL 连接 Keystone
    ↓
Keystone 验证凭据，返回 Token + Service Catalog
    ↓
Service Catalog 包含所有服务的端点信息：
{
  "token": "gAAAAABh...",
  "catalog": [
    {
      "type": "compute",
      "name": "nova",
      "endpoints": [
        {
          "url": "http://192.168.1.100:8774/v2.1",
          "interface": "public",
          "region": "RegionOne"
        }
      ]
    },
    {
      "type": "network",
      "name": "neutron",
      "endpoints": [
        {
          "url": "http://192.168.1.100:9696",
          "interface": "public",
          "region": "RegionOne"
        }
      ]
    },
    ...
  ]
}
    ↓
当调用 api.nova.tenant_quota_get() 时：
    1. 从 request.user.service_catalog 中查找 service_type="compute" 的端点
    2. 使用 Token 访问该端点
    3. 调用 Nova API: GET {nova_url}/os-quota-sets/{tenant_id}
```

#### 服务端点查找（openstack_dashboard/api/base.py）

```python
def url_for(request, service_type, endpoint_type=None, region=None):
    """从 Service Catalog 中查找服务端点 URL"""
    endpoint_type = endpoint_type or settings.OPENSTACK_ENDPOINT_TYPE
    
    # 从用户会话中获取 Service Catalog
    catalog = request.user.service_catalog
    service = get_service_from_catalog(catalog, service_type)
    
    if service:
        if not region:
            region = request.user.services_region
        url = get_url_for_service(service, region, endpoint_type)
        if url:
            return url
    
    raise exceptions.ServiceCatalogException(service_type)

def get_service_from_catalog(catalog, service_type):
    """从 Catalog 中查找指定类型的服务"""
    if catalog:
        for service in catalog:
            if service.get('type') == service_type:
                return service
    return None
```

#### 客户端初始化（openstack_dashboard/api/_nova.py）

```python
@memoized
def cached_novaclient(request, version=None):
    """创建 Nova 客户端实例"""
    # 从 request 中提取认证参数
    (
        username,
        token_id,
        project_id,
        project_domain_id,
        nova_url,      # 从 Service Catalog 动态获取
        auth_url
    ) = get_auth_params_from_request(request)
    
    if version is None:
        version = VERSIONS.get_active_version()['version']
    
    # 创建客户端，使用动态获取的 URL
    c = nova_client.Client(
        version,
        username,
        token_id,
        project_id=project_id,
        project_domain_id=project_domain_id,
        auth_url=auth_url,
        insecure=INSECURE,
        cacert=CACERT,
        http_log_debug=settings.DEBUG,
        auth_token=token_id,
        endpoint_override=nova_url  # 使用从 Catalog 获取的端点
    )
    return c
```

#### 配置要求

**只需配置 Keystone 地址（在 local_settings.py 中）：**
```python
# openstack_dashboard/local/local_settings.py
OPENSTACK_HOST = "192.168.17.113"
OPENSTACK_KEYSTONE_URL = "http://192.168.17.113/identity/v3"

# 不需要配置其他服务的地址！
# Nova、Neutron、Cinder 等服务的地址会自动从 Service Catalog 获取
```

#### 优势

1. **配置集中化**：只需配置 Keystone 地址
2. **服务解耦**：服务地址变化无需修改 Horizon 代码
3. **动态发现**：支持多 Region 和服务迁移
4. **统一认证**：使用 Keystone Token 进行统一认证
5. **灵活部署**：在 DevStack 环境中所有服务自动注册

### 2. API 客户端封装

#### Nova API 结构（openstack_dashboard/api/nova.py 实际代码）
```python
# 从实际文件 openstack_dashboard/api/nova.py 中的导入
import collections
import logging
from operator import attrgetter

from django.utils.translation import gettext_lazy as _
from novaclient import api_versions
from novaclient import exceptions as nova_exceptions
from novaclient.v2 import instance_action as nova_instance_action
from novaclient.v2 import servers as nova_servers

from horizon import exceptions as horizon_exceptions
from horizon.utils import memoized
from openstack_dashboard.api import _nova
from openstack_dashboard.api import base

# API 静态值
INSTANCE_ACTIVE_STATE = 'ACTIVE'
VOLUME_STATE_AVAILABLE = "available"
DEFAULT_QUOTA_NAME = 'default'

# 从 _nova 模块导入的函数
get_microversion = _nova.get_microversion
server_get = _nova.server_get
Server = _nova.Server

def is_feature_available(request, features):
    return bool(get_microversion(request, features))
```

#### 控制台类封装（实际代码）
```python
# openstack_dashboard/api/nova.py 中的实际类定义
class VNCConsole(base.APIDictWrapper):
    """Wrapper for the "console" dictionary.
    
    Returned by the novaclient.servers.get_vnc_console method.
    """
    _attrs = ['url', 'type']

class SPICEConsole(base.APIDictWrapper):
    """Wrapper for the "console" dictionary.
    
    Returned by the novaclient.servers.get_spice_console method.
    """
    _attrs = ['url', 'type']

class SerialConsole(base.APIDictWrapper):
    """Wrapper for the "console" dictionary.
    
    Returned by the novaclient.servers.get_serial_console method.
    """
    _attrs = ['url', 'type']
```

#### 实际的 Nova 客户端实现
Nova 的具体实现在 `openstack_dashboard/api/_nova.py` 文件中，这是内部实现文件。

### 2. 错误处理
```python
try:
    instances = api.nova.server_list(request)
except Exception as e:
    exceptions.handle(request, 
                     _('Unable to retrieve instances: %s') % str(e))
    instances = []
```

## 配置文件系统详解

### 配置文件层级结构和加载顺序

**Horizon 采用分层配置架构，通过 Python 的链式导入实现配置继承和覆盖机制。**

#### 完整的配置加载链条

```
manage.py 启动
    ↓ 设置 DJANGO_SETTINGS_MODULE = "openstack_dashboard.settings"
    ↓
openstack_dashboard/settings.py（主配置文件）
    ↓ from openstack_dashboard.defaults import *
    ↓
openstack_dashboard/defaults.py（应用层默认配置）
    ↓ from horizon.defaults import *
    ↓
horizon/defaults.py（框架层默认配置）
    ↓ from openstack_auth.defaults import *
    ↓
openstack_auth/defaults.py（认证层默认配置）
    ↓
回到 openstack_dashboard/settings.py
    ↓ from local.local_settings import *
    ↓
openstack_dashboard/local/local_settings.py（环境特定配置）
    ↓
openstack_dashboard/local/local_settings.d/*.py（可选配置片段）
```

#### 关键代码示例

**1. manage.py 指定配置模块：**
```python
# manage.py
import os
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "openstack_dashboard.settings")
    execute_from_command_line(sys.argv)
```

**2. settings.py 导入 defaults.py：**
```python
# openstack_dashboard/settings.py（第40行）
from openstack_dashboard.defaults import *  # 导入应用层默认配置
```

**3. defaults.py 导入 horizon.defaults：**
```python
# openstack_dashboard/defaults.py（第21行）
from horizon.defaults import *  # 导入框架层默认配置
```

**4. horizon.defaults 导入 openstack_auth.defaults：**
```python
# horizon/defaults.py（第16行）
from openstack_auth.defaults import *  # 导入认证层默认配置
```

**5. settings.py 最后导入 local_settings.py：**
```python
# openstack_dashboard/settings.py（第242行）
try:
    from local.local_settings import *  # 导入本地配置覆盖
except ImportError:
    _LOG.warning("No local_settings file found.")
```

**6. 可选的配置片段加载：**
```python
# openstack_dashboard/settings.py（第266-280行）
LOCAL_SETTINGS_DIR_PATH = os.path.join(ROOT_PATH, "local", "local_settings.d")
if os.path.exists(LOCAL_SETTINGS_DIR_PATH):
    for (dirpath, dirnames, filenames) in os.walk(LOCAL_SETTINGS_DIR_PATH):
        for filename in sorted(filenames):
            if filename.endswith(".py"):
                try:
                    with open(os.path.join(dirpath, filename), encoding="utf-8") as f:
                        exec(f.read())
                except Exception:
                    _LOG.exception("Can not exec settings snippet %s", filename)
```

#### 配置覆盖机制

**Python 的 `from module import *` 特性：**
- 导入模块中所有不以下划线开头的变量
- **后导入的同名变量会覆盖先前的定义**
- 实现配置的层层覆盖

**配置优先级（从低到高）：**
```
openstack_auth.defaults  ← 最低优先级
    ↓ 被覆盖
horizon.defaults
    ↓ 被覆盖
openstack_dashboard.defaults
    ↓ 被覆盖
openstack_dashboard.settings（主配置）
    ↓ 被覆盖
local.local_settings  ← 最高优先级
    ↓ 被覆盖
local_settings.d/*.py  ← 最终覆盖
```

**实例：SITE_BRANDING 的覆盖链：**
```python
# horizon/defaults.py（第59行）
SITE_BRANDING = _("Horizon")

# openstack_dashboard/defaults.py（第97行）
SITE_BRANDING = 'OpenStack Dashboard'  # 覆盖了 "Horizon"

# local/local_settings.py（你可以再次覆盖）
SITE_BRANDING = '我的云平台'  # 最终显示这个
```

#### 各层配置的职责

| 层级 | 文件 | 职责 | 示例配置 | 版本控制 |
|-----|------|------|---------|---------|
| 认证层 | `openstack_auth/defaults.py` | 认证相关基础配置 | `LOGIN_URL`, `LOGOUT_URL` | ✅ 纳入 Git |
| 框架层 | `horizon/defaults.py` | Horizon 框架配置 | `SITE_BRANDING`, `SESSION_REFRESH` | ✅ 纳入 Git |
| 应用层 | `openstack_dashboard/defaults.py` | OpenStack 特定配置 | `POLICY_FILES`, `SITE_BRANDING` | ✅ 纳入 Git |
| 主配置 | `openstack_dashboard/settings.py` | Django 配置和应用结构 | `MIDDLEWARE`, `INSTALLED_APPS` | ✅ 纳入 Git |
| 环境层 | `local/local_settings.py` | 环境特定配置 | `OPENSTACK_HOST`, `DEBUG` | ❌ 不纳入 Git |

#### 为什么要这样设计？

1. **模块化架构**
   - `openstack_auth/` - 独立的认证模块，可被其他项目使用
   - `horizon/` - 通用的 UI 框架，可独立于 OpenStack 使用
   - `openstack_dashboard/` - 具体的 OpenStack 仪表板应用

2. **关注点分离**
   - 框架维护者管理 `horizon/defaults.py`
   - 应用开发者管理 `openstack_dashboard/defaults.py`
   - 运维人员只需关注 `local/local_settings.py`

3. **环境隔离**
   - 开发、测试、生产环境使用不同的 `local_settings.py`
   - 敏感信息（SECRET_KEY、数据库密码）不提交到版本控制
   - 便于 CI/CD 自动化部署

4. **灵活覆盖**
   - 可以覆盖任何默认配置而不修改框架代码
   - 支持配置片段（`local_settings.d/`）实现模块化配置

### 数据库连接配置

### 重要说明：Horizon 主要使用缓存而非传统数据库

### 1. 实际的数据库配置位置

**默认情况下，Horizon 不使用传统的数据库存储，而是使用缓存和会话：**

```python
# 在 openstack_dashboard/settings.py 中常见的会话/缓存配置（示例）
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    },
}
```

**本地配置文件位置：**
- 主配置：`openstack_dashboard/local/local_settings.py`
- 配置目录：`openstack_dashboard/local/local_settings.d/`

**实际的本地配置示例（openstack_dashboard/local/local_settings.py）：**
```python
# 实际项目中的配置
DEBUG = True
WEBROOT = "/dashboard/"
COMPRESS_OFFLINE = True
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "member"
OPENSTACK_HOST = "192.168.17.113"
OPENSTACK_KEYSTONE_URL = "http://192.168.17.113/identity/v3"
ALLOWED_HOSTS = ["*"]

# 如果需要数据库存储，可以添加：
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(LOCAL_PATH, 'horizon.sqlite3'),
#     }
# }
```

### 2. 会话和缓存配置

```python
# 会话与缓存配置（示例，依分支可能不同）
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    },
}
```

### 3. 为什么 Horizon 主要使用缓存而不是数据库？

1. **无状态设计**：Horizon 主要作为 OpenStack API 的前端界面
2. **性能考虑**：缓存比数据库访问更快
3. **简化部署**：减少数据库依赖，便于横向扩展
4. **数据来源**：大部分数据来自 OpenStack 服务，不需要本地存储

### 4. 配置文件加载顺序（实际代码）

```python
# openstack_dashboard/settings.py 中的常见加载顺序（示例）
from openstack_dashboard.defaults import *  # 1. 加载默认配置

try:
    from local.local_settings import *  # 2. 加载本地配置覆盖
except ImportError:
    _LOG.warning("No local_settings file found.")

# 3. 可选：加载 local_settings.d 目录中的配置片段
LOCAL_SETTINGS_DIR_PATH = os.path.join(ROOT_PATH, "local", "local_settings.d")
if os.path.exists(LOCAL_SETTINGS_DIR_PATH):
    for (dirpath, dirnames, filenames) in os.walk(LOCAL_SETTINGS_DIR_PATH):
        for filename in sorted(filenames):
            if filename.endswith(".py"):
                try:
                    with open(os.path.join(dirpath, filename), encoding="utf-8") as f:
                        exec(f.read())
                except Exception:
                    _LOG.exception("Can not exec settings snippet %s", filename)
```

## 视图函数详解

### 1. 基础视图类型

#### 表格视图 (DataTableView)
```python
class InstancesView(tables.DataTableView):
    table_class = InstancesTable
    template_name = 'project/instances/index.html'
    page_title = _("Instances")
    
    def get_data(self):
        """获取表格数据"""
        instances = []
        try:
            instances = api.nova.server_list(self.request)
        except Exception:
            exceptions.handle(self.request, 
                            _('Unable to retrieve instances.'))
        return instances
```

#### 表单视图 (ModalFormView)
```python
class LaunchInstanceView(workflows.WorkflowView):
    workflow_class = LaunchInstance
    template_name = 'project/instances/launch.html'
    
    def get_initial(self):
        """设置表单初始值"""
        initial = super().get_initial()
        initial['project_id'] = self.request.user.tenant_id
        return initial
```

#### 详情视图 (DetailView)
```python
class DetailView(tabs.TabView):
    tab_group_class = InstanceDetailTabs
    template_name = 'project/instances/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_data()
        context["instance"] = instance
        return context
    
    def get_data(self):
        instance_id = self.kwargs['instance_id']
        try:
            instance = api.nova.server_get(self.request, instance_id)
        except Exception:
            exceptions.handle(self.request, 
                            _('Unable to retrieve instance details.'))
        return instance
```

### 2. URL 路由配置（实际项目结构）

**主 URL 配置（openstack_dashboard/urls.py）：**
```python
# 实际的主 URL 配置文件存在于 openstack_dashboard/urls.py
```

**Dashboard 级别的 URL 配置：**
- Project Dashboard: `openstack_dashboard/dashboards/project/`
- Admin Dashboard: `openstack_dashboard/dashboards/admin/`
- Identity Dashboard: `openstack_dashboard/dashboards/identity/`
- Settings Dashboard: `openstack_dashboard/dashboards/settings/`

**Panel 级别的 URL 配置示例：**
- Instances: `openstack_dashboard/dashboards/project/instances/`
- Volumes: `openstack_dashboard/dashboards/project/volumes/`
- Networks: `openstack_dashboard/dashboards/project/networks/`
- Images: `openstack_dashboard/dashboards/project/images/`

### 3. 路由到页面的最短链路（速查）
1. `openstack_dashboard/urls.py`（主 URLConf）
2. Dashboard/Panel `urls.py`（模块内 URL）
3. `views.py`（Django 视图类/函数）→ 模板（`templates/...`）
4. 前端模块（AngularJS Controller/Service/Directive）
5. REST 接口：`openstack_dashboard/api/rest/*`（Django REST 入口）
6. Python API 封装：`openstack_dashboard/api/*`（nova/neutron/cinder/...）
7. 客户端库调用（novaclient、neutronclient 等）

提示：遇到 404 先查 URL（含 `WEBROOT` 前缀），遇到 403 先查 Policy；数据异常再检查 API 调用链。

## 前端架构

### 1. 技术栈概览

Horizon 采用**混合式前端架构**，结合服务端渲染和客户端动态交互：

#### 核心技术栈
- **Django 模板系统**: 服务端渲染，生成基础 HTML 结构
- **AngularJS 1.x**: 客户端动态交互框架，广泛用于数据表格、表单处理
- **jQuery 3.5+**: DOM 操作、AJAX 请求和事件处理
- **Bootstrap 3.x**: 响应式 UI 组件库和栅格系统
- **SCSS/Sass**: CSS 预处理器，实现模块化样式开发
- **D3.js**: 数据可视化库，用于图表和指标展示
- **XStatic**: Python 包管理器，管理前端依赖库

#### 开发工具链
- **Karma + Jasmine**: JavaScript 单元测试框架
- **ESLint**: JavaScript 代码质量检查工具
- **npm**: Node.js 包管理器，管理开发依赖
- **SCSS 编译器**: 将 SCSS 源文件编译为 CSS

注：依赖版本与脚本名称以本仓库实际 `package.json` 为准；如未定义 `build/watch`，请不要执行相关命令。

### 2. 静态文件组织结构（实际项目结构）

#### 编译后的静态文件目录
```
static/                     # Django collectstatic 后的静态文件
├── app/                   # OpenStack 应用特定静态文件
├── auth/                  # 认证模块静态文件
├── dashboard/             # 仪表板核心静态文件
├── framework/             # AngularJS 框架组件
├── horizon/               # Horizon 核心框架静态文件
├── js/                    # 全局 JavaScript 库
├── scss/                  # 编译后的 CSS 文件
└── themes/                # 主题样式文件
```

#### 源静态文件结构
```
horizon/static/framework/   # AngularJS 框架核心组件
├── conf/                  # 配置模块
│   ├── conf.module.js     # Angular 配置模块
│   └── conf.scss          # 配置相关样式
├── util/                  # 工具函数模块
│   ├── util.module.js     # 工具模块定义
│   ├── filters/           # Angular 过滤器
│   ├── validators/        # 表单验证器
│   └── http/              # HTTP 服务封装
├── widgets/               # UI 组件库
│   ├── action-list/       # 操作列表组件
│   ├── charts/            # 图表组件
│   ├── form/              # 表单组件
│   ├── magic-search/      # 智能搜索组件
│   ├── modal/             # 模态框组件
│   ├── table/             # 数据表格组件
│   ├── toast/             # 消息提示组件
│   └── transfer-table/    # 传输表格组件
└── framework.scss         # 框架核心样式

openstack_dashboard/static/app/  # OpenStack 特定功能
├── core/                  # 核心服务 API 模块
│   ├── cloud-services/    # 云服务抽象层
│   ├── conf/              # 应用配置
│   ├── flavors/           # 规格管理
│   ├── images/            # 镜像服务
│   ├── keypairs/          # 密钥对管理
│   ├── metadata/          # 元数据服务
│   ├── network/           # 网络服务
│   ├── openstack-service-api/ # OpenStack API 封装
│   └── server-groups/     # 服务器组
├── resources/             # 资源管理模块
│   └── os-nova/          # 各种 OpenStack 资源（示例：os-nova、os-glance 等）
└── tech-debt/            # 技术债务处理
```

### 3. AngularJS 架构设计

#### 模块化架构
Horizon 使用 AngularJS 1.x 构建现代化的单页应用组件：

```javascript
// horizon/static/framework/framework.module.js
(function() {
  'use strict';
  
  angular
    .module('horizon.framework', [
      'horizon.framework.conf',
      'horizon.framework.util',
      'horizon.framework.widgets'
    ])
    .config(config)
    .run(run);
    
  config.$inject = ['$compileProvider'];
  function config($compileProvider) {
    // 配置 AngularJS 编译器
    $compileProvider.debugInfoEnabled(horizon.conf.debug);
  }
  
  run.$inject = ['$rootScope'];
  function run($rootScope) {
    $rootScope.$on('$routeChangeError', function() {
      horizon.toast.add('error', gettext('页面加载失败'));
    });
  }
})();
```

#### 服务层架构
```javascript
// API 服务示例
angular
  .module('horizon.app.core.instances')
  .factory('horizon.app.core.instances.service', instanceService);

instanceService.$inject = ['horizon.framework.util.http.service'];
function instanceService(apiService) {
  return {
    getInstances: getInstances,
    getInstance: getInstance,
    createInstance: createInstance,
    deleteInstance: deleteInstance
  };
  
  function getInstances() {
    return apiService.get('/api/nova/servers/');
  }
}
```

#### 组件化开发
```javascript
// 表格组件示例
angular
  .module('horizon.framework.widgets.table')
  .directive('hzTable', hzTable);

function hzTable() {
  return {
    restrict: 'E',
    // 注意：避免硬编码 /static，需与 WEBROOT/STATIC_URL 保持一致
    // 示例：在 DevStack 默认 WEBROOT=/dashboard/ 下，静态路径为 /dashboard/static/
    // 推荐通过已注册的模板路径或使用相对 STATIC_URL 的方式组织模板
    templateUrl: '/dashboard/static/framework/widgets/table/table.html',
    scope: {
      config: '=',
      data: '='
    },
    controller: 'hzTableController',
    controllerAs: 'ctrl'
  };
}
```

## 学习路径建议
### 4. 前端开发工作流程（以 DevStack/Linux 环境为准）

#### 重要提示：开发环境 vs 生产环境

**生产环境/DevStack部署（推荐）：**
```bash
# DevStack中Horizon通过Apache2提供服务，无需单独启动前端
# 访问地址：http://controller/dashboard/

# 修改代码后的部署流程：
cd /opt/stack/horizon
python manage.py collectstatic --noinput    # 收集静态文件
sudo systemctl reload apache2               # 重启Apache2
```

**独立开发环境（调试用）：**
```bash
# 适用于功能开发、调试、前端测试
# 重要：需要先激活虚拟环境！
source /opt/stack/data/venv/bin/activate
cd /opt/stack/horizon
source /opt/stack/devstack/openrc admin admin
python manage.py runserver 0.0.0.0:8000
```

#### DevStack中的实际部署

**Apache 配置示例（/etc/apache2/sites-available/horizon.conf）：**

DevStack 实际生成的配置：
```apache
<VirtualHost *:80>
    WSGIScriptAlias /dashboard /opt/stack/horizon/openstack_dashboard/wsgi.py
    
    # WSGI 进程配置
    WSGIDaemonProcess horizon \
        user=stack \
        group=stack \
        processes=3 \
        threads=10 \
        home=/opt/stack/horizon \
        display-name=%{GROUP}
    
    WSGIApplicationGroup %{GLOBAL}
    WSGIProcessGroup horizon
    
    SetEnv APACHE_RUN_USER stack
    SetEnv APACHE_RUN_GROUP stack
    
    # 静态文件别名
    Alias /dashboard/media /opt/stack/horizon/openstack_dashboard/static
    Alias /dashboard/static /opt/stack/horizon/static
    
    # 根路径重定向到 dashboard
    RedirectMatch "^/$" "/dashboard/"
    
    # 目录权限配置
    <Directory /opt/stack/horizon/>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride None
        <IfVersion >= 2.4>
            Require all granted
        </IfVersion>
    </Directory>
    
    # 日志配置
    ErrorLog /var/log/apache2/horizon_error.log
    LogLevel warn
    CustomLog /var/log/apache2/horizon_access.log combined
</VirtualHost>

# 全局虚拟环境配置（在 VirtualHost 外部）
WSGIPythonHome /opt/stack/data/venv
WSGISocketPrefix /var/run/apache2
```

**关键配置说明：**

1. **WSGIPythonHome（全局配置）**：
   - 位于 `<VirtualHost>` 标签外部
   - 为所有 WSGI 应用指定 Python 虚拟环境
   - 这是 DevStack 的标准配置方式
   - **优势**：如果有多个 WSGI 应用，它们都会使用同一个虚拟环境
   - **替代方式**：也可以在 `WSGIDaemonProcess` 中使用 `python-home` 参数

2. **WSGIDaemonProcess 参数**：
   - `user=stack group=stack`: 运行用户和组
   - `processes=3 threads=10`: 进程和线程数（可根据服务器配置调整）
   - `home=/opt/stack/horizon`: 工作目录（Django 应用的根目录）
   - `display-name=%{GROUP}`: 进程显示名称（便于 `ps` 命令识别）
   - 注意：这里没有 `python-home` 参数，因为使用了全局的 `WSGIPythonHome`

3. **WSGIApplicationGroup %{GLOBAL}**：
   - 使用全局应用组，避免 Python 子解释器问题
   - 推荐配置，特别是使用 C 扩展模块时

4. **静态文件别名**：
   - `/dashboard/media` → `/opt/stack/horizon/openstack_dashboard/static`
   - `/dashboard/static` → `/opt/stack/horizon/static`（collectstatic 收集后的位置）
   - 静态文件由 Apache 直接提供，不经过 Django

5. **WSGISocketPrefix**：
   - 指定 WSGI socket 文件的存储位置
   - 避免默认 `/tmp` 目录可能的权限问题

**两种虚拟环境配置方式对比：**

```apache
# 方式1：全局配置（DevStack 使用的方式）
WSGIPythonHome /opt/stack/data/venv  # 在 VirtualHost 外部

<VirtualHost *:80>
    WSGIDaemonProcess horizon user=stack group=stack processes=3 threads=10
    ...
</VirtualHost>

# 方式2：局部配置（针对特定进程）
<VirtualHost *:80>
    WSGIDaemonProcess horizon \
        python-home=/opt/stack/data/venv \
        user=stack \
        group=stack \
        processes=3 \
        threads=10
    ...
</VirtualHost>
```

**两种方式的区别：**
- 全局配置：影响所有 WSGI 应用，配置更简洁
- 局部配置：每个 WSGI 应用可以使用不同的虚拟环境，更灵活

**验证配置：**
```bash
# 1. 查看虚拟环境配置
grep WSGIPythonHome /etc/apache2/sites-available/horizon.conf
# 输出：WSGIPythonHome /opt/stack/data/venv

# 2. 验证虚拟环境存在
ls -la /opt/stack/data/venv/bin/python3

# 3. 测试配置语法
sudo apache2ctl configtest
# 应该输出：Syntax OK

# 4. 查看 Apache 进程使用的 Python
ps aux | grep "WSGIDaemonProcess horizon" | grep -v grep

# 5. 检查 WSGI 模块是否加载
sudo apache2ctl -M | grep wsgi

# 6. 查看 Apache 错误日志（如有问题）
sudo tail -50 /var/log/apache2/horizon_error.log
```

**常见配置问题：**

1. **路径中的双斜杠**：
   ```apache
   # 如果看到类似这样的路径：
   /opt/stack//horizon
   
   # 虽然不影响功能（系统会自动处理），但可以清理：
   sed -i 's|/opt/stack//|/opt/stack/|g' /etc/apache2/sites-available/horizon.conf
   sudo systemctl reload apache2
   ```

2. **DocumentRoot .blackhole/**：
   ```apache
   DocumentRoot /opt/stack/horizon/.blackhole/
   ```
   - 这是一个空目录，防止直接访问文档根目录
   - 所有请求都通过 WSGIScriptAlias 路由到 Django
   
3. **权限问题**：
   ```bash
   # 确保 stack 用户有权限访问必要的目录
   sudo chown -R stack:stack /opt/stack/horizon
   sudo chmod -R 755 /opt/stack/horizon/static
   ```

#### Apache 配置文件管理机制

**sites-available vs sites-enabled**

Apache 使用两个目录来管理站点配置，这是 Debian/Ubuntu 系统的标准做法：

```
/etc/apache2/
├── sites-available/      # 存放所有可用的站点配置文件
│   ├── 000-default.conf
│   ├── horizon.conf      # 实际配置文件
│   └── other-site.conf
│
└── sites-enabled/        # 存放已启用的站点配置
    ├── 000-default.conf -> ../sites-available/000-default.conf
    └── horizon.conf     -> ../sites-available/horizon.conf  (符号链接)
```

**关键概念：**

1. **sites-available**：配置文件的"仓库"
   - 存放所有站点配置（已启用和未启用的）
   - 是配置文件的实际存储位置
   - 应该编辑这里的文件

2. **sites-enabled**：实际生效的配置
   - 包含指向 `sites-available` 的符号链接
   - **Apache 只加载这个目录中的配置**
   - 通过添加/删除符号链接来启用/禁用站点

**验证符号链接：**

```bash
# 查看 horizon.conf 是否为符号链接
ls -la /etc/apache2/sites-enabled/horizon.conf
# 输出示例：
# lrwxrwxrwx 1 root root 31 May 31 10:51 horizon.conf -> ../sites-available/horizon.conf
#    ↑                                                       ↑
# 符号链接标志 (l)                                      指向实际文件

# 查看符号链接指向的实际路径
readlink -f /etc/apache2/sites-enabled/horizon.conf
# 输出：/etc/apache2/sites-available/horizon.conf
```

**Apache 站点管理命令：**

```bash
# 启用站点（创建符号链接）
sudo a2ensite horizon
# 等同于：sudo ln -s /etc/apache2/sites-available/horizon.conf /etc/apache2/sites-enabled/

# 禁用站点（删除符号链接，但保留配置文件）
sudo a2dissite horizon
# 等同于：sudo rm /etc/apache2/sites-enabled/horizon.conf
# 注意：配置文件仍保留在 sites-available 中

# 列出所有可用的站点
ls /etc/apache2/sites-available/

# 列出已启用的站点
ls /etc/apache2/sites-enabled/

# 测试配置语法
sudo apache2ctl configtest

# 重载配置（应用更改）
sudo systemctl reload apache2

# 重启 Apache（完全重启）
sudo systemctl restart apache2
```

**修改配置的正确流程：**

```bash
# ✅ 正确方式：编辑 sites-available 中的文件
sudo vim /etc/apache2/sites-available/horizon.conf

# 测试配置
sudo apache2ctl configtest

# 重载 Apache
sudo systemctl reload apache2

# ❌ 错误方式：直接编辑 sites-enabled 中的文件
# 虽然符号链接会指向实际文件，但这不是推荐的做法
# 容易混淆配置管理
```

**优势：**

1. **配置管理**：可以保留多个配置文件但不启用
2. **快速切换**：启用/禁用站点只需要创建/删除符号链接
3. **安全备份**：禁用的配置不会丢失
4. **版本控制友好**：可以版本控制 sites-available

**多环境配置示例：**

```bash
# 场景：有开发、测试、生产三个环境的配置
/etc/apache2/sites-available/
├── horizon-prod.conf    # 生产环境
├── horizon-dev.conf     # 开发环境
└── horizon-test.conf    # 测试环境

# 切换到开发环境
sudo a2dissite horizon-prod horizon-test
sudo a2ensite horizon-dev
sudo systemctl reload apache2

# 切换到生产环境
sudo a2dissite horizon-dev horizon-test
sudo a2ensite horizon-prod
sudo systemctl reload apache2

# 临时禁用 Horizon（排错或维护）
sudo a2dissite horizon-prod
sudo systemctl reload apache2
# 配置文件仍保留，需要时可以快速恢复
```

**常用检查命令：**

```bash
# 一键检查当前配置状态
echo "=== Apache 站点配置状态 ==="
echo "可用站点："
ls -1 /etc/apache2/sites-available/
echo ""
echo "已启用站点："
ls -la /etc/apache2/sites-enabled/
echo ""
echo "Horizon 配置链接状态："
readlink -f /etc/apache2/sites-enabled/horizon.conf
echo ""
echo "Apache 配置测试："
sudo apache2ctl configtest
```

**DevStack 部署时的操作：**

```bash
# DevStack 在部署 Horizon 时会：
# 1. 创建配置文件
sudo tee /etc/apache2/sites-available/horizon.conf << 'EOF'
<VirtualHost *:80>
    # ... 配置内容 ...
</VirtualHost>
EOF

# 2. 启用站点
sudo a2ensite horizon

# 3. 重启 Apache
sudo systemctl restart apache2
```

#### 开发环境配置

**DevStack 环境（推荐）：**
```bash
# 1. 激活虚拟环境（必须！）
source /opt/stack/data/venv/bin/activate

# 2. 安装前端依赖
cd /opt/stack/horizon
npm install

# 3. 验证 Python 环境
which python3  # 应该输出：/opt/stack/data/venv/bin/python3
pip list | grep django

# 4. 修改代码后收集静态文件
python manage.py collectstatic --noinput

# 5. 重启 Apache（使更改生效）
sudo systemctl reload apache2

# 6. 或者使用开发服务器调试
source /opt/stack/devstack/openrc admin admin
python manage.py runserver 0.0.0.0:8000
```

**非 DevStack 环境：**
```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt
npm install

# 3. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

#### 不同开发场景的最佳实践

**场景1：纯前端开发（修改CSS、JS、模板）**
```bash
# 在DevStack环境中进行（推荐）
cd /opt/stack/horizon

# 1. 修改静态文件
vim horizon/static/framework/widgets/table/table.scss
vim openstack_dashboard/static/dashboard/scss/components/_tables.scss

# 2. 收集静态文件
python manage.py collectstatic --noinput

# 3. 重启Apache（使更改生效）
sudo systemctl reload apache2

# 4. 访问测试：http://controller/dashboard/
```

**场景2：功能开发（需要后端API支持）**
```bash
# 方法1：在DevStack环境中直接开发（推荐）
cd /opt/stack/horizon
# 修改Python代码后，Apache会自动重载WSGI应用
# 如需查看实时日志：
sudo tail -f /var/log/apache2/error.log

# 方法2：使用开发服务器调试（适合快速迭代）
source /opt/stack/data/venv/bin/activate
cd /opt/stack/horizon
source /opt/stack/devstack/openrc admin admin
python manage.py runserver 0.0.0.0:8000

# 注意：Horizon 不读取 OS_* 环境变量，连接信息在 local_settings.py 中：
# OPENSTACK_HOST、OPENSTACK_KEYSTONE_URL 等
```

**场景3：完全独立开发和测试**
```bash
# 1. 激活虚拟环境
source venv/bin/activate  # 或 /opt/stack/data/venv/bin/activate

# 2. 配置连接到远程OpenStack环境
# 编辑 openstack_dashboard/local/local_settings.py：
cat >> openstack_dashboard/local/local_settings.py << EOF
OPENSTACK_HOST = "remote-controller-ip"
OPENSTACK_KEYSTONE_URL = "http://remote-controller-ip/identity/v3"
DEBUG = True
EOF

# 3. 启动开发服务器
cd /opt/stack/horizon  # 或你的项目目录
python manage.py runserver 0.0.0.0:8000

# 4. 访问：http://localhost:8000
```

#### DevStack环境配置参考

**local.conf中的Horizon配置：**
```ini
[[local|localrc]]
# Horizon相关配置
HORIZON_APACHE_ROOT="/dashboard"
HORIZON_APACHE_CONF="/etc/apache2/sites-available/horizon.conf"

# 开发模式设置
HORIZON_DEBUG=True
HORIZON_COMPRESS_OFFLINE=False

# 允许的主机
HORIZON_ALLOWED_HOSTS="*"
```

**实际目录结构：**
```
/opt/stack/horizon/          # DevStack中的Horizon位置
├── static/                  # collectstatic收集的静态文件
│   ├── app/
│   ├── framework/
│   └── horizon/
├── openstack_dashboard/     # 主应用
├── horizon/                 # 核心框架
└── manage.py               # Django管理脚本
```

#### 性能优化配置

**生产环境静态文件优化：**
```python
# openstack_dashboard/local/local_settings.py
DEBUG = False
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# 静态文件配置
STATIC_ROOT = '/opt/stack/horizon/static/'
STATIC_URL = '/dashboard/static/'

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    },
}
```

#### 常见问题和解决方案

**问题1：静态文件不更新**
```bash
# 解决方案
python manage.py collectstatic --noinput --clear
sudo systemctl reload apache2
```

**问题2：Apache权限问题**
```bash
# 确保Apache用户有权限访问静态文件
sudo chown -R www-data:www-data /opt/stack/horizon/static/
sudo chmod -R 755 /opt/stack/horizon/static/
```

**问题3：SCSS编译失败**
```bash
# 检查 npm 依赖
npm install

# 仅当 package.json 定义了对应脚本时再执行：
npm run build
npm run watch
```

#### 静态文件处理
```bash
# 开发环境
python manage.py collectstatic --noinput    # 收集静态文件
python manage.py compress --force           # 压缩 CSS/JS（生产环境）

# 使用 tox 运行（推荐）
# 启动开发服务器（以 tox -l 输出为准，如无该 env 请使用 manage.py）
tox -e runserver || python manage.py runserver 0.0.0.0:8000
```

#### 代码规范和检查
```bash
# JavaScript 代码检查
npm run lint                               # ESLint 检查
eslint horizon/static --fix                # 自动修复

# Python 代码检查
tox -e pep8                               # PEP8 规范检查
```

### 5. 测试框架

#### JavaScript 单元测试
```bash
# 运行前端测试
npm test                                   # Karma + Jasmine 测试
tox -e npm                                # 使用 tox 运行前端测试

# 测试配置文件
horizon/karma.conf.js                     # Karma 配置
openstack_dashboard/karma.conf.js         # Dashboard 特定测试配置
```

#### 测试代码示例
```javascript
// 测试文件示例：horizon/static/framework/widgets/table/table.spec.js
describe('hzTable directive', function() {
  var $compile, $rootScope;
  
  beforeEach(module('horizon.framework.widgets.table'));
  beforeEach(inject(function(_$compile_, _$rootScope_) {
    $compile = _$compile_;
    $rootScope = _$rootScope_;
  }));
  
  it('should render table with data', function() {
    var scope = $rootScope.$new();
    scope.tableData = [/* test data */];
    
    var element = $compile('<hz-table data="tableData"></hz-table>')(scope);
    scope.$digest();
    
    expect(element.find('tr').length).toBeGreaterThan(0);
  });
});
```

### 6. 前端开发最佳实践

#### SCSS/CSS 开发规范
```scss
// 遵循 BEM 命名规范
.hz-table {
  &__header {
    background-color: $table-header-bg;
    
    &--sortable {
      cursor: pointer;
    }
  }
  
  &__row {
    &:hover {
      background-color: $table-row-hover-bg;
    }
  }
}

// 使用变量和 mixin
@import 'horizon/framework/framework';

$primary-color: #0066cc;
$border-radius: 4px;

@mixin button-variant($color) {
  background-color: $color;
  border-color: darken($color, 10%);
}
```

#### AngularJS 开发规范
```javascript
// 1. 使用 IIFE 模式
(function() {
  'use strict';
  
  angular
    .module('app.module')
    .controller('MyController', MyController);
  
  MyController.$inject = ['$scope', 'dataService'];
  function MyController($scope, dataService) {
    var vm = this;
    vm.items = [];
    vm.loadData = loadData;
    
    activate();
    
    function activate() {
      loadData();
    }
    
    function loadData() {
      dataService.getItems().then(function(data) {
        vm.items = data;
      });
    }
  }
})();
```

#### 性能优化建议
1. **懒加载模块**: 按需加载 AngularJS 模块
2. **图片优化**: 使用适当格式和尺寸的图片
3. **缓存策略**: 合理使用浏览器缓存
4. **代码分割**: 将大型 JavaScript 文件拆分
5. **CSS 优化**: 避免深层嵌套，使用高效的选择器

#### 调试技巧
```javascript
// 1. 使用 Angular Debug 信息
angular.reloadWithDebugInfo();

// 2. 控制台调试
var scope = angular.element('#myElement').scope();
console.log(scope.vm);

// 3. 性能监控
console.time('api-call');
apiService.getData().then(function() {
  console.timeEnd('api-call');
});
```

### 7. 与 Django 后端的集成

#### AJAX API 调用
```javascript
// 使用 Django CSRF Token
angular.module('horizon.framework.util.http')
  .config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common['X-CSRFToken'] = 
      $('input[name=csrfmiddlewaretoken]').val();
  }]);

// API 服务封装
function apiCall(method, url, data) {
  return $http({
    method: method,
    url: url,
    data: data,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
  });
}
```

提示：Horizon 已提供统一的 HTTP 封装（如 `horizon.framework.util.http.service`）并处理 CSRF，建议优先使用内置服务，避免重复配置。

#### 模板集成
```html
<!-- Django 模板中嵌入 AngularJS -->
{% load static %}
<div ng-app="horizon.dashboard.project.instances" ng-strict-di>
  <div ng-controller="InstancesController as ctrl">
    <hz-table 
      config="ctrl.tableConfig" 
      data="ctrl.instances">
    </hz-table>
  </div>
</div>

<script src="{% static 'app/core/instances/instances.module.js' %}"></script>
<script src="{% static 'app/core/instances/instances.controller.js' %}"></script>
```

### 8. 前端架构演进建议

#### 当前架构的优势
- **成熟稳定**: AngularJS 1.x 生态系统完整
- **Django 集成**: 与后端框架深度集成
- **组件丰富**: 大量可复用的 UI 组件
- **测试完备**: 完整的单元测试覆盖

#### 未来发展方向
1. **模块化增强**: 进一步提升组件的独立性和可复用性
2. **性能优化**: 实施代码分割和懒加载策略
3. **开发体验**: 改进构建流程和开发工具
4. **现代化升级**: 考虑向 Vue.js 或 React 迁移的可能性

#### 最佳实践总结
1. **保持模块化**: 每个功能都应该是独立的模块
2. **遵循约定**: 统一的代码风格和命名规范
3. **测试先行**: 为关键功能编写测试
4. **文档完善**: 及时更新技术文档
5. **性能监控**: 定期检查和优化性能瓶颈

### 第一阶段：基础理解 (1-2周)
1. **环境搭建**
   - 安装 DevStack 或使用现有 OpenStack 环境
   - 配置 Horizon 开发环境
   - 熟悉基本的 Django 概念

2. **项目结构熟悉**
   - 浏览项目目录结构
   - 理解 Dashboard/Panel 概念
   - 查看现有功能模块

3. **基础操作**
   - 启动开发服务器
   - 访问 Web 界面
   - 尝试基本的云资源操作

### 第二阶段：深入理解 (2-3周)
1. **核心代码阅读**
   - 阅读 `horizon/base.py` 了解 Dashboard 和 Panel 基类
   - 分析 `openstack_dashboard/dashboards/project/instances/` 完整实现
   - 理解 `openstack_dashboard/api/nova.py` API 调用流程

2. **组件学习**
   - 学习 `horizon/tables/` 表格组件的使用
   - 理解 `horizon/forms/` 和 `horizon/workflows/` 组件
   - 掌握 `horizon/templates/` 模板系统

3. **API 集成**
   - 学习 `openstack_dashboard/api/` 目录下的 API 封装
   - 理解 `openstack_auth/` 认证和权限机制
   - 掌握 `horizon/exceptions.py` 错误处理模式

### 第三阶段：实践开发 (3-4周)
1. **简单定制**
   - 修改 `openstack_dashboard/dashboards/project/instances/` 页面显示
   - 在现有表格中添加新列
   - 自定义 `openstack_dashboard/themes/` 主题样式

2. **功能扩展**
   - 在 `openstack_dashboard/dashboards/project/` 下创建新 Panel
   - 实现自定义 Action 和 Form
   - 在 `openstack_dashboard/api/` 中添加新的 API 调用

3. **插件开发**
   - 开发独立的 Dashboard 插件
   - 在 `openstack_dashboard/enabled/` 中配置启用
   - 实现完整的 CRUD 操作

### 第四阶段：高级开发 (4-6周)
1. **性能优化**
   - 实现缓存机制
   - 优化 API 调用
   - 前端性能调优

2. **安全加固**
   - 实现权限控制
   - 添加安全检查
   - 防止常见安全漏洞

3. **测试和部署**
   - 编写单元测试
   - 集成测试
   - 生产环境部署

## 二次开发指南

### 1. 创建自定义 Dashboard
```python
# my_dashboard/dashboard.py
import horizon

class MyDashboard(horizon.Dashboard):
    name = _("My Dashboard")
    slug = "mydashboard"
    panels = ('mypanel',)
    default_panel = 'mypanel'
    permissions = ('openstack.roles.admin',)

horizon.register(MyDashboard)
```

### 2. 创建自定义 Panel
```python
# my_dashboard/mypanel/panel.py
import horizon
from my_dashboard import dashboard

class MyPanel(horizon.Panel):
    name = _("My Panel")
    slug = "mypanel"

dashboard.MyDashboard.register(MyPanel)
```

### 3. 实现视图和表格
```python
# my_dashboard/mypanel/views.py
from horizon import tables
from . import tables as my_tables

class IndexView(tables.DataTableView):
    table_class = my_tables.MyTable
    template_name = 'mydashboard/mypanel/index.html'
    
    def get_data(self):
        # 实现数据获取逻辑
        return []
```

### 4. 配置启用（实际项目中的 enabled 目录）

**实际的 enabled 配置目录：**
- `openstack_dashboard/enabled/` - 全局功能开关
- `openstack_dashboard/local/enabled/` - 本地功能开关

**配置文件示例：**
```python
# openstack_dashboard/enabled/_50_mydashboard.py
DASHBOARD = 'mydashboard'
DISABLED = False
ADD_INSTALLED_APPS = ['my_dashboard']
```

**实际项目中的一些 enabled 文件：**
- 各种 Panel 和 Dashboard 的启用配置
- 功能特性的开关控制
- 插件的注册和管理

### 5. 部署到 DevStack 环境

#### 完整的部署流程

**重要前提：配置数据库连接**

在部署自定义报表功能之前，需要确保已在本地配置文件中添加数据库连接信息：

```python
# openstack_dashboard/local/local_settings.py

# 自定义报表使用的数据库配置（复用 devstack MySQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'horizon_custom',      # MySQL数据库名称
        'USER': 'root',                # MySQL用户名
        'PASSWORD': 'secret',          # MySQL密码
        'HOST': '127.0.0.1',           # MySQL主机地址
        'PORT': '3306',                # MySQL端口
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
}
```

**第1步：准备环境（数据库）**

在 DevStack 主机上创建数据库（只需执行一次）：

```bash
# 连接到 MySQL
mysql -uroot -psecret -h127.0.0.1

# 在 MySQL 提示符下执行：
CREATE DATABASE horizon_custom DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

**第2步：准备文件**

假设你在本地开发了一个自定义 Dashboard，文件结构如下：
```
<你的项目>/openstack_dashboard/dashboards/custom_reports/
├── __init__.py
├── dashboard.py
├── models.py                    # 新增：数据库模型
├── resource_usage/
│   ├── __init__.py
│   ├── panel.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
└── static/

<你的项目>/openstack_dashboard/enabled/_60_custom_reports.py
<你的项目>/openstack_dashboard/local/local_settings.py  # 包含 DATABASES 配置
```

**第3步：复制文件到 DevStack Horizon 目录**

```bash
# 1. 找到 DevStack 的 Horizon 目录
cd /opt/stack/horizon

# 2. 复制 Dashboard 目录
sudo cp -r <你的项目>/openstack_dashboard/dashboards/custom_reports \
           /opt/stack/horizon/openstack_dashboard/dashboards/

# 3. 复制启用配置文件
sudo cp <你的项目>/openstack_dashboard/enabled/_60_custom_reports.py \
        /opt/stack/horizon/openstack_dashboard/enabled/

# 4. 复制本地配置文件（包含数据库配置）
sudo cp <你的项目>/openstack_dashboard/local/local_settings.py \
        /opt/stack/horizon/openstack_dashboard/local/

# 5. 设置正确的权限
sudo chown -R stack:stack /opt/stack/horizon/openstack_dashboard/dashboards/custom_reports
sudo chown stack:stack /opt/stack/horizon/openstack_dashboard/enabled/_60_custom_reports.py
sudo chown stack:stack /opt/stack/horizon/openstack_dashboard/local/local_settings.py
```

**第4步：执行数据库迁移**

```bash
# 1. 激活虚拟环境（关键！）
source /opt/stack/data/venv/bin/activate

# 2. 进入 Horizon 目录
cd /opt/stack/horizon

# 3. 生成迁移文件（为自定义模型创建迁移）
python manage.py makemigrations custom_reports

# 4. 执行迁移（在数据库中创建表）
python manage.py migrate

# 5. 验证表是否创建成功（可选）
mysql -uroot -psecret -h127.0.0.1 -e "USE horizon_custom; SHOW TABLES;"
# 应该看到：tenant_resource_snapshot

# 如果 migrate 失败，检查：
# - 数据库连接是否正常
# - local_settings.py 中的 DATABASES 配置是否正确
# - MySQL 服务是否运行
```

**第5步：收集静态文件**

```bash
cd /opt/stack/horizon

# 收集静态文件到 static/ 目录
python manage.py collectstatic --noinput

# 如果有自定义 CSS/JS，可能需要强制重新收集
python manage.py collectstatic --noinput --clear

# 压缩静态文件（生产环境）
python manage.py compress --force
```

**第6步：重启服务**

```bash
# 方法1：重启 Apache2（推荐）
sudo systemctl restart apache2

# 或者只重载配置（更快）
sudo systemctl reload apache2

# 方法2：检查 Apache 状态
sudo systemctl status apache2

# 方法3：查看 Apache 错误日志（排错用）
sudo tail -f /var/log/apache2/error.log
```

**第7步：验证部署**

```bash
# 1. 检查文件是否存在
ls -la /opt/stack/horizon/openstack_dashboard/dashboards/custom_reports/
ls -la /opt/stack/horizon/openstack_dashboard/enabled/_60_custom_reports.py

# 2. 检查静态文件
ls -la /opt/stack/horizon/static/app/

# 3. 访问 Web 界面
# 浏览器访问：http://<controller-ip>/dashboard/
# 登录后应该能看到新的 Dashboard
```

#### 常见部署问题和解决方案

**问题1：Dashboard 不显示**

```bash
# 检查启用配置是否正确
cat /opt/stack/horizon/openstack_dashboard/enabled/_60_custom_reports.py

# 确保 DISABLED = False
# 检查 Python 语法错误
python -m py_compile /opt/stack/horizon/openstack_dashboard/enabled/_60_custom_reports.py

# 重启 Apache
sudo systemctl restart apache2
```

**问题2：静态文件404**

```bash
# 重新收集静态文件
cd /opt/stack/horizon
python manage.py collectstatic --noinput --clear

# 检查 Apache 配置中的静态文件路径
# 注意：应该查看 sites-available，这是配置文件的实际位置
cat /etc/apache2/sites-available/horizon.conf | grep Alias

# 应该有类似这样的配置：
# Alias /dashboard/media /opt/stack/horizon/openstack_dashboard/static
# Alias /dashboard/static /opt/stack/horizon/static

# 验证静态文件目录存在且有内容
ls -la /opt/stack/horizon/static/

# 检查 Apache 配置语法
sudo apache2ctl configtest
```

**问题3：权限错误**

```bash
# 确保 Apache 用户（通常是 www-data）有权限读取文件
sudo chown -R www-data:www-data /opt/stack/horizon/static/
sudo chmod -R 755 /opt/stack/horizon/static/

# 检查 Python 文件权限
sudo chown -R stack:stack /opt/stack/horizon/openstack_dashboard/
```

**问题4：Python 模块导入错误**

```bash
# 激活虚拟环境并测试导入
source /opt/stack/data/venv/bin/activate
cd /opt/stack/horizon
python manage.py shell

>>> from openstack_dashboard.dashboards.custom_reports import dashboard
>>> print(dashboard.CustomReports)
# 如果报错，检查 __init__.py 是否存在和 Python 语法
```

**问题6：实例资源详情不显示（已修复）**

```bash
# 症状：综合资源概览页面中"实例资源占用详情"部分为空，但 OpenStack 中已创建实例
# 原因：api.nova.server_list() 返回的是元组 (servers, has_more_data)，而不是直接的列表

# 错误写法：
instances = api.nova.server_list(self.request)  # 这会得到元组而不是列表

# 正确写法（已修复）：
instances, has_more = api.nova.server_list(self.request)  # 解包元组获取服务器列表

# 验证修复：
# 1. 确认已更新 views.py 第 147 行
# 2. 重新部署代码
# 3. 刷新页面查看实例列表
```

**问题7：虚拟环境未激活**

```bash
# 症状：ImportError, ModuleNotFoundError
# 解决方案：

# 1. 确认虚拟环境路径
sudo cat /etc/apache2/sites-available/horizon.conf | grep WSGIPythonHome
# 输出：WSGIPythonHome /opt/stack/data/venv

# 2. 激活虚拟环境
source /opt/stack/data/venv/bin/activate

# 3. 验证
which python3
pip list | grep django

# 4. 如果包缺失，重新安装
cd /opt/stack/horizon
pip install -r requirements.txt
```

**问题5：API 调用失败**

```bash
# 检查 local_settings.py 配置
cat /opt/stack/horizon/openstack_dashboard/local/local_settings.py

# 确认以下配置正确：
# OPENSTACK_HOST = "controller_ip"
# OPENSTACK_KEYSTONE_URL = "http://controller_ip/identity/v3"

# 测试 Keystone 连接
curl http://controller_ip/identity/v3
```

#### 快速部署脚本

创建一个部署脚本 `deploy.sh`：

```bash
#!/bin/bash
# Horizon 自定义 Dashboard 部署脚本

set -e

HORIZON_DIR="/opt/stack/horizon"
SOURCE_DIR="<你的项目路径>"
DASHBOARD_NAME="custom_reports"

echo "开始部署 Horizon Dashboard..."

# 1. 复制文件
echo "复制 Dashboard 文件..."
sudo cp -r "${SOURCE_DIR}/openstack_dashboard/dashboards/${DASHBOARD_NAME}" \
           "${HORIZON_DIR}/openstack_dashboard/dashboards/"

echo "复制启用配置..."
sudo cp "${SOURCE_DIR}/openstack_dashboard/enabled/_60_${DASHBOARD_NAME}.py" \
        "${HORIZON_DIR}/openstack_dashboard/enabled/"

# 2. 设置权限
echo "设置文件权限..."
sudo chown -R stack:stack "${HORIZON_DIR}/openstack_dashboard/dashboards/${DASHBOARD_NAME}"
sudo chown stack:stack "${HORIZON_DIR}/openstack_dashboard/enabled/_60_${DASHBOARD_NAME}.py"

# 3. 激活虚拟环境并收集静态文件
echo "激活虚拟环境..."
source /opt/stack/data/venv/bin/activate
echo "Python 路径: $(which python3)"

echo "收集静态文件..."
cd "${HORIZON_DIR}"
python manage.py collectstatic --noinput

# 4. 重启 Apache
echo "重启 Apache..."
sudo systemctl restart apache2

echo "部署完成！"
echo "请访问: http://$(hostname -I | awk '{print $1}')/dashboard/"
```

#### 开发环境与生产环境对比

| 场景 | 开发环境 | DevStack/生产环境 |
|------|---------|------------------|
| 启动方式 | `python manage.py runserver` | Apache2 + mod_wsgi |
| 静态文件 | Django 自动处理 | 需要 `collectstatic` |
| 代码热重载 | 自动重载 | 需要重启 Apache |
| 配置文件 | 本地 `local_settings.py` | DevStack 生成的配置 |
| 调试 | `DEBUG = True` | `DEBUG = False` |
| 性能 | 较慢 | 优化后的生产性能 |
| 适用场景 | 功能开发、调试 | 实际部署、测试 |

#### 持续开发工作流

```bash
# 1. 激活虚拟环境
source /opt/stack/data/venv/bin/activate

# 2. 在本地修改代码
vim openstack_dashboard/dashboards/custom_reports/resource_usage/views.py

# 3. 测试（可选）
cd /opt/stack/horizon
python manage.py test openstack_dashboard.dashboards.custom_reports

# 4. 部署到 DevStack
./deploy.sh

# 5. 查看日志排错（如需要）
sudo tail -f /var/log/apache2/error.log

# 6. 或者使用开发服务器快速测试
source /opt/stack/devstack/openrc admin admin
python manage.py runserver 0.0.0.0:8000

# 7. 清理浏览器缓存，刷新页面查看效果
```

#### 维护和数据清理

**数据清理管理命令**

自定义报表系统会持续保存资源快照到数据库，需要定期清理旧数据以避免数据库膨胀：

```bash
# 1. 激活虚拟环境
source /opt/stack/data/venv/bin/activate

# 2. 进入 Horizon 目录
cd /opt/stack/horizon

# 3. 清理30天前的快照数据（默认保留30天）
python manage.py cleanup_old_snapshots --days=30

# 4. 模拟运行（不实际删除，查看会删除多少数据）
python manage.py cleanup_old_snapshots --days=30 --dry-run

# 5. 清理60天前的数据（保留更长时间）
python manage.py cleanup_old_snapshots --days=60
```

**配置定时清理（推荐）**

使用 cron 定期自动清理：

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每天凌晨2点清理30天前的数据）
0 2 * * * cd /opt/stack/horizon && source /opt/stack/data/venv/bin/activate && python manage.py cleanup_old_snapshots --days=30 >> /var/log/horizon/cleanup.log 2>&1

# 或者每周日凌晨3点清理
0 3 * * 0 cd /opt/stack/horizon && source /opt/stack/data/venv/bin/activate && python manage.py cleanup_old_snapshots --days=30 >> /var/log/horizon/cleanup.log 2>&1
```

**查看清理日志**

```bash
# 创建日志目录（如果不存在）
sudo mkdir -p /var/log/horizon
sudo chown stack:stack /var/log/horizon

# 查看清理日志
tail -f /var/log/horizon/cleanup.log

# 查看最近的清理记录
tail -n 50 /var/log/horizon/cleanup.log
```

**监控数据库大小**

```bash
# 查看快照表的数据量
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT tenant_id) as total_tenants,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record
FROM tenant_resource_snapshot;
"

# 查看各租户的快照数量
mysql -uroot -psecret -h127.0.0.1 -e "
USE horizon_custom;
SELECT 
    tenant_id,
    COUNT(*) as snapshot_count,
    MIN(created_at) as first_snapshot,
    MAX(created_at) as last_snapshot
FROM tenant_resource_snapshot
GROUP BY tenant_id
ORDER BY snapshot_count DESC
LIMIT 10;
"

# 查看表大小
mysql -uroot -psecret -h127.0.0.1 -e "
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = 'horizon_custom'
    AND table_name = 'tenant_resource_snapshot';
"
```

**环境变量永久配置（可选）：**

如果希望每次登录自动激活虚拟环境：

```bash
# 编辑 ~/.bashrc
cat >> ~/.bashrc << 'EOF'
# Horizon 开发环境
if [ -f /opt/stack/data/venv/bin/activate ]; then
    source /opt/stack/data/venv/bin/activate
fi

# OpenStack 环境变量
if [ -f /opt/stack/devstack/openrc ]; then
    source /opt/stack/devstack/openrc admin admin
fi
EOF

# 重新加载配置
source ~/.bashrc

# 验证
which python3  # 应该输出：/opt/stack/data/venv/bin/python3
```

## 常见问题和解决方案

### 1. 开发环境问题
- **静态文件不更新**: 运行 `python manage.py collectstatic`
- **权限错误**: 检查 OpenStack 服务配置和用户权限
- **API 调用失败**: 验证服务端点和认证信息

### 2. 性能问题
- **页面加载慢**: 实现适当的缓存机制
- **API 超时**: 增加超时设置，优化查询条件
- **内存占用高**: 检查数据查询范围，实现分页

### 3. 部署问题
- **静态文件路径**: 配置正确的 STATIC_ROOT 和 STATIC_URL
- **数据库连接**: 确保数据库配置正确
- **Web 服务器配置**: 正确配置 Apache/Nginx

### 快速自检清单

#### Python 环境检查
- ✅ 虚拟环境是否已激活？`which python3` 应该输出 `/opt/stack/data/venv/bin/python3`
- ✅ Apache 配置是否指定虚拟环境？
  ```bash
  grep WSGIPythonHome /etc/apache2/sites-available/horizon.conf
  # 应输出：WSGIPythonHome /opt/stack/data/venv
  # 注意：应该在 </VirtualHost> 标签之外（全局配置）
  ```
- ✅ Django 和依赖包是否安装？`pip list | grep django`
- ✅ manage.py 的 shebang 是否正确？`head -n 1 /opt/stack/horizon/manage.py`
- ✅ Apache WSGI 模块是否加载？`sudo apache2ctl -M | grep wsgi`

#### 配置检查
- ✅ WEBROOT 是否与访问路径一致（默认 `/dashboard/`）？
- ✅ `local_settings.py` 中 `OPENSTACK_HOST`、`OPENSTACK_KEYSTONE_URL` 是否正确？
- ✅ OpenStack 环境变量是否加载？`source /opt/stack/devstack/openrc admin admin`
- ✅ `tox -l` 是否确认了实际可用的环境名称？

#### Apache 配置检查
- ✅ sites-enabled/horizon.conf 是否为符号链接？
  ```bash
  ls -la /etc/apache2/sites-enabled/horizon.conf
  # 应该显示：lrwxrwxrwx ... horizon.conf -> ../sites-available/horizon.conf
  ```
- ✅ 修改配置时是否编辑 sites-available 而非 sites-enabled？
- ✅ Apache 配置语法是否正确？`sudo apache2ctl configtest`
- ✅ Horizon 站点是否已启用？`ls /etc/apache2/sites-enabled/ | grep horizon`

#### 静态文件和路径检查
- ✅ 是否避免硬编码 `/static`，而使用与 `WEBROOT/STATIC_URL` 一致的路径？
- ✅ 静态文件是否收集？`ls -la /opt/stack/horizon/static/`
- ✅ Apache 静态文件别名是否配置正确？
  ```bash
  grep "Alias /dashboard" /etc/apache2/sites-available/horizon.conf
  ```

#### 权限和错误检查
- ✅ 403 问题是否首先检查了 Policy 配置与面板权限？
- ✅ 404 问题是否检查了 URLConf 与前缀（`/dashboard/`）？
- ✅ Python 模块导入错误是否检查了虚拟环境和 __init__.py？
- ✅ Apache 错误日志显示什么？`sudo tail -f /var/log/apache2/horizon_error.log`

## 总结

Horizon 是一个功能强大且灵活的 Web 仪表板框架。通过系统的学习和实践，你可以：

1. **理解架构**: 掌握 Django + OpenStack API 的架构模式
2. **熟练开发**: 能够开发自定义功能和插件
3. **性能优化**: 了解如何优化性能和用户体验
4. **生产部署**: 掌握生产环境的部署和维护

建议按照学习路径循序渐进，多动手实践，结合官方文档和社区资源，逐步成为 Horizon 开发专家。

## 参考资源

- [官方文档](https://docs.openstack.org/horizon/latest/)
- [开发者指南](https://docs.openstack.org/horizon/latest/contributor/)
- [API 参考](https://docs.openstack.org/api-ref/)
- [Django 文档](https://docs.djangoproject.com/)
- [OpenStack 客户端库](https://docs.openstack.org/python-openstackclient/latest/)