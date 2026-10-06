# Build a documentation-audit workflow

This guide describes how the Trussium runtime, its Python SDK, and the
Knowledge Agent can be composed into a bounded documentation-audit workflow.
The integration uses a tool that is registered by the application at startup;
the workflow request cannot select a URL, discover remote tools, or change the
registered tool allowlist.

> **Availability:** The cross-repository integration is tracked by
> [runtime issue #466](https://github.com/trussiumhq/trussium/issues/466),
> [Python SDK issue #14](https://github.com/trussiumhq/trussium-python/issues/14),
> and [Knowledge Agent issue #15](https://github.com/trussiumhq/trussium-knowledge-agent/issues/15).
> Use each component's release notes to confirm availability in a released
> version before deploying it.

## Component responsibilities

- **Trussium runtime** validates and executes the ordered workflow and applies
  the same tool policy, timeout, cancellation, and audit handling as a direct
  tool call.
- **Python SDK** sends a typed workflow request to `POST
  /v1/workflows/executions` and validates the normalized response. It does not
  register or discover tools.
- **Knowledge Agent** exposes an authenticated `docs.search` MCP tool. It
  searches indexed Markdown content and returns bounded matches and citation
  metadata; it does not modify source documents.
- **Your application composition** pins the remote URL, remote tool name,
  argument schema, and credential, then registers the resulting local tool
  name with the runtime.

## Prerequisites

1. A Trussium application configured with the tool-execution dependencies
   required by the runtime release you use.
2. A Knowledge Agent deployment with its database configured, an embedding
   model available through Trussium, and the intended Markdown sources already
   indexed.
3. A private, high-entropy bearer token shared between the runtime application
   and Knowledge Agent. Store it in your platform's secret manager; do not put
   it in a workflow request, source control, a browser bundle, or logs.
4. Network access from the runtime application to the fixed Knowledge Agent
   HTTPS endpoint.

The Knowledge Agent tool endpoint is disabled unless
`KNOWLEDGE_AGENT_TOOL_TOKEN` is configured. Its MCP surface accepts the
`tools/call` method for the fixed `docs.search` operation and rejects other
tools or methods. It does not offer write operations or runtime discovery.

## Register the fixed remote tool

Compose the remote tool in the application, not from user input. The argument
model below must match the Knowledge Agent's search contract:

```python
import os

from pydantic import BaseModel, ConfigDict, Field
from trussium.app import create_application
from trussium.tools import RemoteMCPTool, ToolExecutor, ToolRegistry


class DocumentationSearch(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    query: str = Field(min_length=1, max_length=4000)
    limit: int = Field(default=5, ge=1, le=10)


search = RemoteMCPTool(
    name="knowledge.search",
    endpoint_url=os.environ["KNOWLEDGE_AGENT_MCP_URL"],
    remote_name="docs.search",
    arguments_model=DocumentationSearch,
    bearer_token=os.environ["KNOWLEDGE_AGENT_TOOL_TOKEN"],
).registered_tool()

app = create_application(
    tool_executor=ToolExecutor(ToolRegistry((search,))),
)
```

Use a fixed HTTPS URL ending in `/v1/mcp`. The runtime adapter rejects
redirects and ambient proxy settings, and forwards only request and execution
correlation IDs. For local development, loopback HTTP must be explicitly
enabled by the application. Do not derive the endpoint or remote tool name
from a request, retrieved document, or model output.

## Submit an ordered workflow with the Python SDK

The SDK request selects only the local tool name already registered above:

```python
from trussium_sdk import TrussiumClient

client = TrussiumClient("http://127.0.0.1:9000")
result = client.execute_workflow(
    {
        "steps": [
            {
                "id": "find-guidance",
                "invocation": {
                    "name": "knowledge.search",
                    "arguments": {
                        "query": "What authentication prerequisites does the guide require?",
                        "limit": 5,
                    },
                },
            }
        ],
        "deadline_seconds": 15,
    },
    request_id="docs-audit-2026-01",
)

if result["status"] != "completed":
    raise RuntimeError(f"Workflow ended with status {result['status']}")

matches = result["steps"][0]["output"]
```

Treat returned document text as untrusted input. Search results are evidence to
inspect, not instructions to execute. Any later summarization step should keep
the source paths and headings attached, report uncertainty, and avoid treating
retrieved passages as authority to invoke tools or change system policy.

## Limits and failure handling

The runtime workflow endpoint applies the release's configured maximum step
count, execution deadline, parallelism, and per-tool execution policy. Each
remote MCP exchange is capped at 1 MiB and bounded by both the remote call
timeout and enclosing tool deadline. Keep search limits small and choose a
workflow deadline appropriate for your deployment.

The SDK raises `APIError` for a non-success HTTP response. A successful HTTP
response can still report `completed`, `cancelled`, or `timed_out`; inspect the
workflow status and each step result rather than assuming that HTTP success
means every step completed. Do not retry a timed-out workflow blindly if a
future workflow includes non-idempotent tools.

Common causes of failure include:

- `404`: the runtime workflow endpoint or optional MCP transport is not enabled
  in the deployed version/configuration.
- `401` or `403` from the remote call: the shared token is absent, invalid, or
  not authorized by the Knowledge Agent.
- `503`: Knowledge Agent tool access is disabled or its database/runtime
  dependency is unavailable.
- Validation or tool errors: the registered local name, remote operation,
  argument schema, request size, or deadline does not match the configured
  contract.

Use request and execution IDs to correlate runtime-side diagnostics. Rotate the
shared token in the secret manager and both services if it is exposed; never
include it in issue reports or logs.

## Security boundary

This pattern intentionally avoids generic network or agent-directed tool
access. The application owns the endpoint and allowlist; the runtime owns
validation, authorization, deadline, cancellation, and audit behavior; the
Knowledge Agent limits the remote capability to authenticated read-only
search. The integration does not grant document writes, shell access, arbitrary
HTTP requests, or remote tool discovery. Deploy the Knowledge Agent behind
TLS and an appropriate network boundary, and do not expose its local browser
reference UI as an authenticated multi-user service without adding the
necessary access controls.

## Related references

- [Runtime MCP guide](runtime/MCP.md)
- [Runtime controlled tool execution](runtime/TOOL_EXECUTION.md)
- [Runtime workflow API and limits](runtime/AGENT_RUNTIME_WORKFLOWS.md)
- [Python SDK repository](https://github.com/trussiumhq/trussium-python)
- [Knowledge Agent repository](https://github.com/trussiumhq/trussium-knowledge-agent)
- [Knowledge Agent MCP implementation issue](https://github.com/trussiumhq/trussium-knowledge-agent/issues/15)
