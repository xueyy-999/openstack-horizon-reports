# OpenStack Horizon 自定义报表系统（openstack-horizon-reports）

本仓库基于 **OpenStack Horizon** 二次开发，新增 **“自定义报表（Custom Reports）”** Dashboard 模块，用于对计算/存储/网络等资源进行可视化展示、配额使用率分析与历史趋势查看，提升运维观测与管理效率。

## 功能概览

- 资源概览
  - 实例/CPU/内存配额与使用量
  - 卷/容量/快照配额与使用量
  - 网络/浮动IP/路由器/安全组配额与使用量
- 可视化图表
  - 配额使用率对比（柱状图）
  - 资源占用分布（环形图）
  - 历史趋势分析（按时间维度）
- 历史数据
  - 访问页面时自动写入资源快照
  - 支持查询最近 N 天数据（默认 30 天）

## 目录结构（关键改动）

- `openstack_dashboard/dashboards/custom_reports/`
  - 自定义 Dashboard 主模块（Views/Models/Templates/Static）
- `openstack_dashboard/enabled/_60_custom_reports.py`
  - Horizon Dashboard 启用入口
- `horizon部署文档.md`
  - 部署、迁移、静态文件收集、验证与排障流程

## 快速开始（DevStack 环境）

1. 安装 DevStack 并确保 Horizon 可访问。
2. 将本仓库代码/自定义模块同步到 DevStack 的 Horizon 源码目录。
3. 按部署文档执行数据库迁移与静态文件收集。

详细步骤请直接看：

- `horizon部署文档.md`

## 访问入口

- Horizon：`http://<devstack-host>/dashboard/`
- Keystone：`http://<devstack-host>/identity/`

## 截图

- 建议把截图放到 `docs/screenshots/`
- 然后在这里插入：

```text
docs/screenshots/menu.png
docs/screenshots/overview.png
docs/screenshots/usage.png
```

## 说明

- 本仓库用于展示 Horizon 二次开发与自定义报表模块实现。
- 如需用于生产，请结合企业安全策略完善鉴权、审计、告警、备份与权限隔离。
