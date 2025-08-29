# Dify on MySQL

[English](README.md) | 简体中文

## 项目背景

自2024年10月起，我们开始与 Dify 团队展开合作。考虑到 MySQL 是全球应用最广泛的关系型数据库之一，许多用户强烈希望 Dify 能够支持 MySQL。同时，由于 OceanBase 与 MySQL 具有高度兼容性，我们向 Dify 项目提交了支持 MySQL pull request。但由于 Dify 团队当时正专注于内部开发里程碑的工作，暂时无法处理这项贡献。

此外，通过与众多 Dify 用户的深入交流，我们发现市场对多项企业级功能存在强烈需求。幸运的是，OceanBase 能够提供这些能力。因此，我们持续自主维护并增强该分支功能，以满足这些企业级需求。

## 欢迎贡献

欢迎任何建议，并感谢所有的贡献。

## 核心优势

这个分支提供以下企业级特性：

### 高可用性

在生产环境中，系统必须提供 7x24 小时不间断服务。数据库作为整个系统的核心组件，其任何故障都可能严重影响服务可用性。

OceanBase 通过 Paxos 共识协议保障高可用性。在生产环境中以集群模式部署时，即使单台服务器甚至多台服务器发生故障，只要集群中多数派仍然运行，OceanBase 仍能始终保持服务状态，确保无任何数据丢失（RPO = 0），并实现故障恢复时间在8秒以内（RTO < 8）。

### 可扩展性

随着运行时间的累积，数据库中存储的数据量持续增长。在传统数据库系统中，一旦数据量超过单台机器的容量限制，扩展就变得极具挑战性。

OceanBase 作为一款流行的分布式数据库，通过向集群添加新的节点来提供无限扩展能力。系统实现了数据和负载的自动重新平衡，整个过程对应用程序完全透明。

### AI 增强

鉴于 OceanBase 也是一款流行的向量数据库，它提供了强大的混合查询能力。这使得在单个查询中可以同时处理多种数据类型，包括向量数据、标量数据（关系表中的传统结构化数据）、GIS 和全文索引。

这种混合查询能力不仅可以帮助提升 AI 查询性能(将过去的多次查询融合为单次查询, 并利用优化器选择最优执行路径)，更为关键的是，通过混合查询可以提升查询的准确度（召回率），特别是在检索增强生成（RAG）系统中发挥更大的价值。

### 降低成本

通过用 OceanBase 替换当前 Dify 使用的所有数据库（包括 PostgreSQL、Weaviate 和 Redis），用户可以实现更高效的资源利用，并显著降低硬件成本。

此外，这种整合简化了数据库运维操作，从运维三套系统减少到只运维一套系统，从而大幅简化了维护工作并降低了操作复杂性。

### 多租户支持

由于 OceanBase 原生支持多租户，Dify 用户现在可以通过 OceanBase 的多租户功能在应用层面实现多租户，而不会影响 Dify 现有的多租户规则。

## 安装社区版

### 系统要求

在安装 Dify 之前，请确保您的机器满足以下最低系统要求：

- CPU >= 2 核
- 内存 >= 8 GiB

### 快速启动

启动 Dify 服务器的最简单方法是运行我们的 [docker-compose.yaml](docker/docker-compose.yaml) 文件。

在运行安装命令之前，请确保您的机器上已安装 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。

启动服务的操作如下：

```bash
cd docker
bash setup-mysql-env.sh
docker compose up -d
```

说明：
- `setup-mysql-env.sh` 是一个设置参数的辅助脚本，它会根据用户输入设置数据库连接信息，并配置 OceanBase 作为向量存储。
- Dify 1.x 开始引入了插件系统，安装插件的过程会根据插件配置执行类似 `python install -r requirements.txt` 的命令。为了加快安装速度，脚本中设置了 `PIP_MIRROR_URL` 为清华大学 Tuna 镜像源。
- 对于中国大陆用户，可以参考 https://github.com/dongyubin/DockerHub 设置 Docker 镜像加速，以获得更好的镜像加载速度。

运行后，可以在浏览器中访问 [http://localhost/install](http://localhost/install) 进入 Dify 控制台并开始初始化安装操作。

更多关于 Dify 使用的信息请参考 [https://dify.ai](https://dify.ai)。

## 许可证

本仓库遵循 [Dify Open Source License](LICENSE) 开源协议，该许可证本质上是 Apache 2.0，但有一些额外的限制。