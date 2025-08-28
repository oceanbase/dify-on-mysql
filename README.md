# Dify for MySQL

English | [简体中文](README_CN.md)

## Why fork

Beginning in October 2024, we initiated a collaboration with the Dify Team. Given that MySQL is one of the most widely used databases worldwide, many users have expressed a strong desire for Dify to support MySQL. At the same time, owing to OceanBase’s high compatibility with MySQL, we submitted a pull request to the Dify project to introduce MySQL support. However, due to the Dify team’s ongoing commitments to their internal development milestones, they were unable to incorporate this contribution at the time.

Furthermore, through extensive discussions with numerous Dify users, we identified significant demand for several enterprise-level features. Fortunately, OceanBase is capable of delivering these capabilities. As a result, we have continued to maintain and enhance this branch independently to meet these enterprise requirements.

## Welcome contribution
We welcome any suggestions and greatly appreciate your contributions.

## Benefits
This branch can provide several enterprise features:
### High Availability
In a production environment, AI platforms must deliver 7x24 uninterrupted service. As the database is a critical component of the entire system, any failure in the database layer can severely disrupt service availability.

OceanBase ensures high availability through the Paxos consensus protocol. When deployed in cluster mode under production conditions, OceanBase remains fully operational even if individual nodes fail. It guarantees a Recovery Point Objective (RPO) of zero and achieves an industry-leading Recovery Time Objective (RTO) of under 8 seconds.

### Scalable
As operational time accumulates, the volume of data stored in the database continues to grow. In legacy systems, once data size exceeds the capacity of a single machine, scaling becomes significantly challenging.

OceanBase, as a distributed database, offers seamless scalability by allowing new nodes to be added to the cluster effortlessly. This enables automatic rebalancing of both data and workload. Moreover, the entire process remains completely transparent to the application.

### AI enhancement
Given that OceanBase also functions as a vector database, it offers powerful hybrid search capabilities. This enables support for multiple data types—including vector data, scalar data (traditional structured data in relational tables), GIS, and full-text content—within a single query.

Such integration enhances both the accuracy and performance of AI-driven queries, making it particularly valuable for Retrieval-Augmented Generation (RAG) systems.

### Reduce Cost
By replacing all databases currently used in Dify—including PostgreSQL, Weaviate, and Redis—with OceanBase, users can achieve more efficient resource utilization and significantly reduce hardware costs.

Furthermore, this consolidation simplifies database operations by eliminating the need to manage three distinct database systems, thereby streamlining maintenance and reducing operational complexity.

### Multi-Tenant
Due to OceanBase's native support for multi-tenancy, Dify users can now try multi-tenant by OceanBase's multi-tenantcy  without compromising Dify’s existing multi-tenant rules.


## Quick start

> Before installing Dify, make sure your machine meets the following minimum system requirements:
>
> - CPU >= 2 Core
> - RAM >= 8 GiB

The easiest way to start the Dify server is through [docker-compose.yaml](docker/docker-compose.yaml). 

Before running Dify with the following commands, make sure that [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed on your machine.

```bash
cd docker
bash setup-mysql-env.sh
docker compose up -d
```

After running, you can access the Dify dashboard in your browser at [http://localhost/install](http://localhost/install) and start the initialization process.

Note:
- setup-mysql-env.sh is a script for setting database parameters. It will update the parameters for database connection according to the user input and set OceanBase as the Vector Store.
- Dify 1.x introduced the plugin system. The plugin installation process will execute commands like `pip install -r requirements.txt` according to the plugin configuration, in order to speed up the installation process, the script has set `PIP_MIRROR_URL` to Tsinghua University Tuna Mirror Site. 


## License

This repository is available under the [Dify Open Source License](LICENSE), which is essentially Apache 2.0 with a few additional restrictions.
