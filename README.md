# MemoryCloud Community

A self-hostable personal memory server for AI agents.

MemoryCloud lets agents store, install, sync, and retrieve long-term memory through Agent Memory Protocol (AMP). Community Edition is designed for personal/private memory nodes. For the public registry, verified memory packages, team workspace, handoff, managed updates, backups, and zero-ops hosting, use MemoryCloud Cloud.

## Choose Your Path

### Use MemoryCloud Cloud

Recommended for most users:

- No server setup.
- Official MemoryCloud Registry.
- Verified memory packages.
- One-link agent install and handoff.
- Agent identity and human binding.
- Runtime updates and Memory Brief.
- Backups, monitoring, email/SMS, audit logs, and zero ops.

Cloud: https://yuemingai.com

### Self-host Community Edition

Recommended for privacy-sensitive users and protocol developers:

- Personal/private memory server.
- AMP-compatible Agent API.
- Local Memory Suite storage.
- Agent API keys.
- Basic Memory Brief and runtime context.
- Local workspace and install credentials.
- Docker Compose deployment.

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000.

Docker:

```bash
cp .env.example .env
docker compose up --build
```

## What Is Open

- Agent Memory Protocol (AMP).
- Memory Suite format: `MEMORY.md`, `DREAMS.md`, manifests, and archives.
- Self-hostable FastAPI server.
- SQLite storage.
- Human and Agent registration.
- API key authentication.
- Basic Memory Brief.
- Memory Suite upload/download/sync.
- Local workspace and project handoff primitives.
- Agent onboarding docs and examples.

## What Cloud Adds

Community Edition gives you a private memory node. MemoryCloud Cloud gives you the public memory network:

- Official public Registry.
- Public Workspace and verified packages.
- Cross-user Agent identity.
- Human-Agent binding across projects.
- One-link memory install and handoff.
- Team workspace, collaboration, and audit.
- Runtime instruction updates.
- Managed backups, monitoring, email/SMS delivery, rate limits, and abuse controls.
- Enterprise controls and Private Cloud options.

See [Cloud vs Community](docs/CLOUD_VS_COMMUNITY.md).

## Core Concepts

- **AMP**: Agent Memory Protocol, the API contract for agent memory operations.
- **Memory Suite**: installable memory package with content, tools, provenance, license, and manifest.
- **Memory Brief**: compact task-start context returned to an Agent.
- **Runtime Context**: persisted project/workspace summary for later sessions.
- **Workspace**: local private memory space in Community; team/network workspace in Cloud.

## Environment

Minimal local configuration:

```bash
APP_ENV=development
PUBLIC_SITE_ORIGIN=http://127.0.0.1:8000
SECRET_KEY=dev-change-me
DATA_ROOT=.memorycloud-data
DATABASE_PATH=.memorycloud-data/platform.sqlite3
STORAGE_DIR=.memorycloud-data/archives
SMS_DRY_RUN=true
EMAIL_DRY_RUN=true
```

For production self-hosting, configure your own HTTPS reverse proxy, SMTP delivery, backups, secret management, and monitoring.

## Tests

```bash
pytest
```

## License

MemoryCloud Community is licensed under the GNU Affero General Public License v3.0. Commercial licenses are available for teams and companies that need different terms.
