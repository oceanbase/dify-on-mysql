# Dify for MySQL

[English](README.md) | 简体中文

这是一个 [https://github.com/langgenius/dify](https://github.com/langgenius/dify)  的 fork，我们基于原始的 Dify 项目进行了一些修改，使其能够使用 MySQL 作为基础数据库，同时可以使用mysql cache作为缓存。

本分支基于历史版本 [https://github.com/oceanbase-devhub/dify](https://github.com/oceanbase-devhub/dify)，自 Dify 1.1.0 开始更新，后续将在官方社区加入 MySQL 适配前进行定期发布。

## 安装社区版

### 系统要求

在安装 Dify 之前，请确保您的机器满足以下最低系统要求：

- CPU >= 2 Core
- RAM >= 4 GiB

### 快速启动

启动 Dify 服务器的最简单方法是运行我们的 [docker-compose.yaml](docker/docker-compose.yaml) 文件。

在运行安装命令之前，请确保您的机器上安装了 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。

启动服务的操作如下：

```bash
cd docker
bash setup-mysql-env.sh
docker compose up -d
```

说明：
- setup-mysql-env.sh 是一个设置参数的辅助脚本，它会根据用户输入设置数据库连接信息，并设置 OceanBase 作为 Vector Store。
- Dify 1.x 开始引入了插件系统，安装插件的过程会根据插件配置执行类似 `python install -r requirements.txt` 的命令，为了加快安装速度，脚本中设置了 `PIP_MIRROR_URL` 为清华大学 Tuna 镜像源网站。
- 对于中国大陆用户，可以参考 https://github.com/dongyubin/DockerHub 设置 docker 镜像加速，以获得更好的镜像加载速度。

运行后，可以在浏览器上访问 [http://localhost/install](http://localhost/install) 进入 Dify 控制台并开始初始化安装操作。

<<<<<<< HEAD
更多关于 Dify 使用的信息请参考 [https://dify.ai](https://dify.ai)。
=======
### 自定义配置

如果您需要自定义配置，请参考 [.env.example](docker/.env.example) 文件中的注释，并更新 `.env` 文件中对应的值。此外，您可能需要根据您的具体部署环境和需求对 `docker-compose.yaml` 文件本身进行调整，例如更改镜像版本、端口映射或卷挂载。完成任何更改后，请重新运行 `docker-compose up -d`。您可以在[此处](https://docs.dify.ai/getting-started/install-self-hosted/environments)找到可用环境变量的完整列表。

#### 使用 Helm Chart 或 Kubernetes 资源清单（YAML）部署

使用 [Helm Chart](https://helm.sh/) 版本或者 Kubernetes 资源清单（YAML），可以在 Kubernetes 上部署 Dify。

- [Helm Chart by @LeoQuote](https://github.com/douban/charts/tree/master/charts/dify)
- [Helm Chart by @BorisPolonsky](https://github.com/BorisPolonsky/dify-helm)
- [Helm Chart by @magicsong](https://github.com/magicsong/ai-charts)
- [YAML 文件 by @Winson-030](https://github.com/Winson-030/dify-kubernetes)
- [YAML file by @wyy-holding](https://github.com/wyy-holding/dify-k8s)

- [🚀 NEW! YAML 文件 (支持 Dify v1.6.0) by @Zhoneym](https://github.com/Zhoneym/DifyAI-Kubernetes)



#### 使用 Terraform 部署

使用 [terraform](https://www.terraform.io/) 一键将 Dify 部署到云平台

##### Azure Global
- [Azure Terraform by @nikawang](https://github.com/nikawang/dify-azure-terraform)

##### Google Cloud
- [Google Cloud Terraform by @sotazum](https://github.com/DeNA/dify-google-cloud-terraform)

#### 使用 AWS CDK 部署

使用 [CDK](https://aws.amazon.com/cdk/) 将 Dify 部署到 AWS

##### AWS 
- [AWS CDK by @KevinZhao](https://github.com/aws-samples/solution-for-deploying-dify-on-aws)

#### 使用 阿里云计算巢 部署

使用 [阿里云计算巢](https://computenest.console.aliyun.com/service/instance/create/default?type=user&ServiceName=Dify%E7%A4%BE%E5%8C%BA%E7%89%88) 将 Dify 一键部署到 阿里云

#### 使用 阿里云数据管理DMS 部署

使用 [阿里云数据管理DMS](https://help.aliyun.com/zh/dms/dify-in-invitational-preview) 将 Dify 一键部署到 阿里云


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=langgenius/dify&type=Date)](https://star-history.com/#langgenius/dify&Date)


## Contributing

对于那些想要贡献代码的人，请参阅我们的[贡献指南](https://github.com/langgenius/dify/blob/main/CONTRIBUTING.md)。
同时，请考虑通过社交媒体、活动和会议来支持 Dify 的分享。

> 我们正在寻找贡献者来帮助将 Dify 翻译成除了中文和英文之外的其他语言。如果您有兴趣帮助，请参阅我们的[i18n README](https://github.com/langgenius/dify/blob/main/web/i18n/README.md)获取更多信息，并在我们的[Discord 社区服务器](https://discord.gg/8Tpq4AcN9c)的`global-users`频道中留言。

**Contributors**

<a href="https://github.com/langgenius/dify/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=langgenius/dify" />
</a>

## 社区与支持

我们欢迎您为 Dify 做出贡献，以帮助改善 Dify。包括：提交代码、问题、新想法，或分享您基于 Dify 创建的有趣且有用的 AI 应用程序。同时，我们也欢迎您在不同的活动、会议和社交媒体上分享 Dify。

- [GitHub Discussion](https://github.com/langgenius/dify/discussions). 👉：分享您的应用程序并与社区交流。
- [GitHub Issues](https://github.com/langgenius/dify/issues)。👉：使用 Dify.AI 时遇到的错误和问题，请参阅[贡献指南](CONTRIBUTING.md)。
- [电子邮件支持](mailto:hello@dify.ai?subject=[GitHub]Questions%20About%20Dify)。👉：关于使用 Dify.AI 的问题。
- [Discord](https://discord.gg/FngNHpbcY7)。👉：分享您的应用程序并与社区交流。
- [X(Twitter)](https://twitter.com/dify_ai)。👉：分享您的应用程序并与社区交流。
- [商业许可](mailto:business@dify.ai?subject=[GitHub]Business%20License%20Inquiry)。👉：有关商业用途许可 Dify.AI 的商业咨询。

## 安全问题

为了保护您的隐私，请避免在 GitHub 上发布安全问题。发送问题至 security@dify.ai，我们将为您做更细致的解答。
>>>>>>> 1.5.0

## License

本仓库遵循 [Dify Open Source License](LICENSE) 开源协议，该许可证本质上是 Apache 2.0，但有一些额外的限制。