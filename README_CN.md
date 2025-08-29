# Dify for MySQL

[English](README.md) | 简体中文

## 为什么要 fork

从 2024 年 10 月开始，我们与 Dify 团队开展了合作。由于 MySQL 是全球使用最广泛的数据库之一，许多用户强烈希望 Dify 支持 MySQL。同时，由于 OceanBase 与 MySQL 的高度兼容性，我们向 Dify 项目提交了引入 MySQL 支持的拉取请求。然而，由于 Dify 团队对内部开发里程碑的持续承诺，他们当时无法纳入这一贡献。

此外，通过与众多 Dify 用户的广泛讨论，我们发现了对几个企业级功能的重大需求。幸运的是，OceanBase 能够提供这些功能。因此，我们继续独立维护和增强此分支，以满足这些企业需求。

## 欢迎贡献
我们欢迎任何建议，并非常感谢您的贡献。

## 企业级特性
此分支可以提供几个企业级特性：

### 高可用性
在生产环境中，AI 平台必须提供 7x24 不间断服务。由于数据库是整个系统的关键组件，数据库层的任何故障都可能严重影响服务可用性。

OceanBase 通过 Paxos 共识协议确保高可用性。在生产条件下以集群模式部署时，即使单个节点发生故障，OceanBase 仍可保持完全运行。它保证恢复点目标 (RPO) 为零，并实现行业领先的恢复时间目标 (RTO) 低于 8 秒。

### 可扩展性
随着运行时间的积累，数据库中存储的数据量不断增长。在传统系统中，一旦数据大小超过单机容量，扩展就会变得非常具有挑战性。

OceanBase 作为分布式数据库，通过允许无缝添加新节点到集群来提供可扩展性。这实现了数据和负载的自动重新平衡。此外，整个过程对应用程序完全透明。

### AI 增强
由于 OceanBase 也充当向量数据库，它提供了强大的混合搜索功能。这支持在单个查询中支持多种数据类型——包括向量数据、标量数据（关系表中的传统结构化数据）、GIS 和全文内容。

这种集成增强了 AI 驱动查询的准确性和性能，使其特别适用于检索增强生成 (RAG) 系统。

### 降低成本
通过用 OceanBase 替换 Dify 中当前使用的所有数据库——包括 PostgreSQL、Weaviate 和 Redis，用户可以实现更高效的资源利用并显著降低硬件成本。

此外，这种整合通过消除管理三个不同数据库系统的需要来简化数据库操作，从而简化维护并降低运营复杂性。

### 多租户
由于 OceanBase 原生支持多租户，Dify 用户现在可以在不影响 Dify 现有多租户规则的情况下通过 OceanBase 的多租户功能尝试多租户。

## 安装社区版

### 系统要求

> 在安装 Dify 之前，请确保您的机器满足以下最低系统要求：
>
> - CPU >= 2 Core
> - RAM >= 8 GiB

### 快速启动

启动 Dify 服务器的最简单方法是通过 [docker-compose.yaml](docker/docker-compose.yaml)。

在运行以下命令之前，请确保您的机器上安装了 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。

```bash
cd docker
bash setup-mysql-env.sh
docker compose up -d
```

运行后，您可以在浏览器中访问 [http://localhost/install](http://localhost/install) 进入 Dify 控制台并开始初始化过程。

注意：
- setup-mysql-env.sh 是一个用于设置数据库参数的脚本。它将根据用户输入更新数据库连接参数，并将 OceanBase 设置为向量存储。
- Dify 1.x 引入了插件系统。插件安装过程将根据插件配置执行类似 `pip install -r requirements.txt` 的命令，为了加快安装过程，脚本已将 `PIP_MIRROR_URL` 设置为清华大学 Tuna 镜像站点。

更多关于 Dify 使用的信息请参考 [https://dify.ai](https://dify.ai)。

## License

本仓库遵循 [Dify Open Source License](LICENSE) 开源协议，该许可证本质上是 Apache 2.0，但有一些额外的限制。