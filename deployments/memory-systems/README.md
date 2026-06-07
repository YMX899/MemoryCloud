# AMP 本地记忆系统部署

本目录用于 Top 10 记忆系统的本地服务组部署。平台会通过 API 生成 compose 文件：

```bash
curl -fsS http://127.0.0.1:18085/api/memory/local-deployments/compose.yml -o docker-compose.yml
curl -fsS http://127.0.0.1:18085/api/memory/local-deployments/env.example -o .env
```

启动后，每个本地记忆运行时只绑定 `127.0.0.1`，外部访问统一走 AMP：

```text
/memory-routes/mem0
/memory-routes/graphiti
/memory-routes/openviking
/memory-routes/supermemory
/memory-routes/letta
/memory-routes/agentmemory
/memory-routes/cognee
/memory-routes/memvid
/memory-routes/hindsight
/memory-routes/memori
```

健康检查：

```bash
curl http://127.0.0.1:18085/memory-routes/agentmemory/health
curl http://127.0.0.1:18085/api/memory/local-deployments/health
```

当前服务器已有 Docker，但未安装 `docker compose` 插件。可以安装插件后使用平台生成的 compose 文件，或使用每个系统的 `native_commands` 原生命令启动到指定端口。

本目录下的 `adapters/amp_local_memory_runtime.py` 是 AMP 内置本地运行时，提供 SQLite 持久化、`/health`、`/ingest`、`/search`、`/export` 以及 Top 10 系统常见路由别名。`adapters/local_memory_stub.py` 只保留为旧路径兼容入口。

真实上游项目要替换内置运行时时，保持同一端口和同一路由合约即可：

1. 上游服务仍绑定 `127.0.0.1:18110-18119`。
2. 平台公开访问仍走 `/memory-routes/{integration_id}`。
3. 先通过 `/api/memory/local-deployments/health` 和 `/memory-routes/{integration_id}/health` 验证可达。
4. OpenViking、Memori 等有许可门槛的项目先做 license review，再进入闭源商业部署。
