# Deploy the Trussium Knowledge Agent

The [Trussium Knowledge Agent](https://github.com/trussiumhq/trussium-knowledge-agent)
is an open-source Python reference application for searching explicitly
selected Markdown sources with retrieval-augmented generation (RAG). It uses
PostgreSQL with pgvector for indexed chunks and a separately operated Trussium
runtime for embeddings and chat.

This guide summarizes the local/self-hosted container path. It does not deploy
a managed public service. The repository's
[container deployment guide](https://github.com/trussiumhq/trussium-knowledge-agent/blob/main/docs/CONTAINER_DEPLOYMENT.md)
is the canonical source for commands, persistence, recovery, and troubleshooting.

## What runs

The Compose stack contains:

- The Knowledge Agent FastAPI app and its CLI in a Python 3.12 container.
- PostgreSQL 17 with pgvector for indexed content.
- Separate persistent volumes for PostgreSQL data and the source lifecycle
  journal.

The Trussium runtime is not part of this stack. Configure the app with an
embedding-enabled runtime model for indexing/search and a chat-enabled model for
answer generation. Configure an API credential only when the runtime requires
one.

Private GitHub access is not required to run the application or index local and
public sources. Public GitHub snapshots are explicit and tokenless. The
optional private GitHub App connector requires operator-managed credentials
and additional setup; keep it disabled unless you deliberately configure it.

## Start a local demo

Clone the repository, copy its example environment, and replace the database
password with a fresh value. Set model names for your Trussium runtime. For a
runtime running on the Docker host, the Compose-specific runtime address is
`http://host.docker.internal:9000` by default; use the `TRUSSIUM_CONTAINER_URL`
setting for a different address.

```bash
cp .env.example .env
openssl rand -hex 24
# Put the generated value in POSTGRES_PASSWORD in .env.
docker compose up -d --build
docker compose ps
curl --fail --silent --show-error http://127.0.0.1:8000/health/live
```

The sample corpus is synthetic and included in the application image. Index it
and try retrieval or a grounded question:

```bash
docker compose run --rm app trussium-knowledge-agent index /app/fixtures/evaluation-corpus
docker compose run --rm app trussium-knowledge-agent search "how do I configure retries?" --limit 5
docker compose run --rm app trussium-knowledge-agent ask "How do I configure retries?" --limit 5
```

The liveness endpoint checks only that the application process can respond; it
does not check PostgreSQL, pgvector, the configured models, or runtime health.
The CLI can index an explicitly mounted local Markdown repository or fetch a
bounded public GitHub snapshot. Use the linked canonical deployment guide for
those workflows and their limits.

## Network and data safety

By default, the app port (`8000`) and database port (`5433`) bind to loopback on
the Docker host. The browser UI has no built-in authentication. Do not expose it
directly to an untrusted network; a deployment serving other users needs a
designed authentication/authorization boundary, TLS, request limits, abuse and
cost controls, and appropriate network policy.

Compose persists the database and lifecycle journal in separate named volumes.
`docker compose down` preserves them; `docker compose down --volumes` deletes
them. Back up both stores and follow the documented coordinated restore order
before exposing a recovered database. Local Docker volumes are not backups or
high availability.

## Further reading

- [Canonical container deployment guide](https://github.com/trussiumhq/trussium-knowledge-agent/blob/main/docs/CONTAINER_DEPLOYMENT.md)
- [Self-hosted operations, backup, and recovery](https://github.com/trussiumhq/trussium-knowledge-agent/blob/main/docs/OPERATIONS.md)
- [Browser interface and security boundary](https://github.com/trussiumhq/trussium-knowledge-agent/blob/main/docs/WEB_INTERFACE.md)
- [Knowledge Agent roadmap](https://github.com/trussiumhq/trussium-knowledge-agent/blob/main/docs/ROADMAP.md)
