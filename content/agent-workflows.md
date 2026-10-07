# Build a documentation-audit workflow

This guide describes how the Trussium runtime, its Python SDK, and the
Knowledge Agent can be composed into a bounded documentation-audit workflow.
The integration uses tools that are registered by the application at startup;
the workflow request cannot select a URL, discover remote tools, or change the
registered tool allowlist.

> **Availability:** The integration implementation is merged across the
> [runtime](https://github.com/trussiumhq/trussium/pull/468),
> [Python SDK](https://github.com/trussiumhq/trussium-python/pull/15), and
> [Knowledge Agent search integration](https://github.com/trussiumhq/trussium-knowledge-agent/pull/16)
> repositories. The deterministic link-audit tool was added in [Knowledge Agent
> PR #20](https://github.com/trussiumhq/trussium-knowledge-agent/pull/20).
> These components are independently released, so verify that the runtime,
> Python SDK, and Knowledge Agent versions you deploy include the features you
> use. Consult each component's release notes; merged code is not by itself a
> guarantee that a feature is available in a published release.

## Component responsibilities

- **Trussium runtime** validates and executes the ordered workflow and applies
  the same tool policy, timeout, cancellation, and audit handling as a direct
  tool call.
- **Python SDK** sends a typed workflow request to `POST
  /v1/workflows/executions` and validates the normalized response. It does not
  register or discover tools.
- **Knowledge Agent** exposes authenticated, fixed read-only MCP tools:
  `docs.search` searches indexed Markdown and returns bounded cited matches;
  `docs.audit_links` deterministically checks local Markdown links and heading
  anchors under an operator-configured root. Neither tool modifies documents.
- **Your application composition** pins the remote URL, remote tool name,
  argument schema, and credential, then registers the resulting local tool
  name with the runtime.

## Prerequisites

1. A Trussium application configured with the tool-execution dependencies
   required by the runtime release you use.
2. For `docs.search`: a Knowledge Agent deployment with its database
   configured, an embedding model available through Trussium, and the intended
   Markdown sources already indexed. These are not required for the standalone
   `docs.audit_links` check.
3. A private, high-entropy bearer token shared between the runtime application
   and Knowledge Agent. Store it in your platform's secret manager; do not put
   it in a workflow request, source control, a browser bundle, or logs.
4. Network access from the runtime application to the fixed Knowledge Agent
   HTTPS endpoint.
5. For `docs.audit_links`, configure `KNOWLEDGE_AGENT_AUDIT_ROOT` on the
   Knowledge Agent service to a readable local Markdown directory. In a
   container deployment, mount the selected documentation into the Knowledge
   Agent service; the runtime workflow cannot provide a filesystem path.

The Knowledge Agent tool endpoint is disabled unless
`KNOWLEDGE_AGENT_TOOL_TOKEN` is configured. Its MCP surface accepts the
`tools/call` method for the fixed `docs.search` and `docs.audit_links`
operations and rejects other tools or methods. `docs.audit_links` also remains
unavailable until the operator configures `KNOWLEDGE_AGENT_AUDIT_ROOT`. The
endpoint does not offer write operations or runtime discovery.

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

## Register the fixed read-only link audit

The link audit is deterministic and does not use a language model or the
Knowledge Agent's retrieval database. Keep its root in trusted service
configuration, and register only the bounded `max_findings` argument:

```python
import os

from pydantic import BaseModel, ConfigDict, Field
from trussium.app import create_application
from trussium.tools import RemoteMCPTool, ToolExecutor, ToolRegistry


class DocumentationAudit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_findings: int = Field(default=100, ge=1, le=500)


audit = RemoteMCPTool(
    name="knowledge.audit-links",
    endpoint_url=os.environ["KNOWLEDGE_AGENT_MCP_URL"],
    remote_name="docs.audit_links",
    arguments_model=DocumentationAudit,
    bearer_token=os.environ["KNOWLEDGE_AGENT_TOOL_TOKEN"],
).registered_tool()

app = create_application(
    tool_executor=ToolExecutor(ToolRegistry((audit,))),
)
```

The Knowledge Agent, not the runtime request, selects the root with
`KNOWLEDGE_AGENT_AUDIT_ROOT`. Callers cannot pass a path, URL, or glob. The
scanner checks inline Markdown links and images, local target existence, and
heading/HTML anchors. It ignores external URLs, does not follow symlinks, and
does not modify source files. Reference-style links and raw HTML links are not
currently audited. Limits are 2,000 Markdown files, 20,000 links, 5 MiB per
file, 50 MiB total input, and at most 500 findings. The requested
`max_findings` further caps the response.

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

To run the deterministic link check instead, submit its explicitly registered
local audit tool. The output reports files and links checked, whether the
finding list was truncated, and each finding's rule ID, source-relative path,
line, target, and explanation:

```python
result = client.execute_workflow(
    {
        "steps": [
            {
                "id": "audit-links",
                "invocation": {
                    "name": "knowledge.audit-links",
                    "arguments": {"max_findings": 100},
                },
            }
        ],
        "deadline_seconds": 15,
    },
    request_id="docs-link-audit-1",
)

if result["status"] != "completed":
    raise RuntimeError(f"Workflow ended with status {result['status']}")

audit_report = result["steps"][0]["output"]
for finding in audit_report["findings"]:
    print(finding["source_path"], finding["line"], finding["rule_id"])
```

Treat findings as review input: the tool identifies suspicious links but never
repairs files or opens external destinations.

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
- `503`: Knowledge Agent tool access is disabled. For `docs.search`, also check
  its database and runtime embedding dependencies.
- Audit service unavailable/failed: confirm the Knowledge Agent has a readable
  `KNOWLEDGE_AGENT_AUDIT_ROOT`, the source is within file/byte/link limits, and
  Markdown files are UTF-8. The generic failure response intentionally omits
  local paths and document content.
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
Knowledge Agent limits remote capabilities to authenticated read-only search
and deterministic local link checks. The integration does not grant document
writes, shell access, arbitrary HTTP requests, or remote tool discovery. Deploy
the Knowledge Agent behind TLS and an appropriate network boundary, and do not
expose its local browser reference UI as an authenticated multi-user service
without adding the necessary access controls.

## Related references

- [Runtime MCP guide](runtime/MCP.md)
- [Runtime controlled tool execution](runtime/TOOL_EXECUTION.md)
- [Runtime workflow API and limits](runtime/AGENT_RUNTIME_WORKFLOWS.md)
- [Python SDK repository](https://github.com/trussiumhq/trussium-python)
- [Knowledge Agent repository](https://github.com/trussiumhq/trussium-knowledge-agent)
- [Knowledge Agent MCP implementation issue](https://github.com/trussiumhq/trussium-knowledge-agent/issues/15)
- [Knowledge Agent read-only link audit](https://github.com/trussiumhq/trussium-knowledge-agent/issues/19)
