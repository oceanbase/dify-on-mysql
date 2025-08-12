# Dify for MySQL

English | [简体中文](README_CN.md)

This is a fork of [https://github.com/langgenius/dify](https://github.com/langgenius/dify) . We made some modifications based on the original Dify project to enable it to use MySQL as the database.

This branch is based on the legacy version [https://github.com/oceanbase-devhub/dify](https://github.com/oceanbase-devhub/dify) and has been maintained since Dify 1.1.0. It will be released regularly before the official community implements MySQL adaptation.

## Quick start

> Before installing Dify, make sure your machine meets the following minimum system requirements:
>
> - CPU >= 2 Core
> - RAM >= 4 GiB

The easiest way to start the Dify server is through [docker-compose.yaml](docker/docker-compose.yaml). 

Before running Dify with the following commands, make sure that [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed on your machine.

```bash
cd docker
bash setup-mysql-env.sh
docker compose up -d
```

Note:
- setup-mysql-env.sh is a script for setting database parameters. It will update the parameters for database connection according to the user input and set OceanBase as the Vector Store.
- Dify 1.x introduced the plugin system. The plugin installation process will execute commands like `pip install -r requirements.txt` according to the plugin configuration, in order to speed up the installation process, the script has set `PIP_MIRROR_URL` to Tsinghua University Tuna Mirror Site. 
- For users in China mainland, you can refer to https://github.com/dongyubin/DockerHub to set the docker mirror for a better image loading speed.

After running, you can access the Dify dashboard in your browser at [http://localhost/install](http://localhost/install) and start the initialization process.

For more information on using Dify, please refer to [https://dify.ai](https://dify.ai).

## License

This repository is available under the [Dify Open Source License](LICENSE), which is essentially Apache 2.0 with a few additional restrictions.
