# Trussium

![Trussium logo](assets/trussium-logo.svg){ width="156" }

## Cloud-native runtime for AI applications

Trussium is a provider-neutral runtime for operating AI capabilities across
hosted providers and private models. It gives applications one HTTP API and
one operational contract while allowing providers, models, and deployment
environments to change independently.

The runtime is designed for teams that need normalized capability responses,
request correlation, streaming support, health and readiness checks, metrics,
tracing, structured logs, and bounded shutdown behavior.

## Project components

### Runtime

The [Trussium runtime](https://github.com/trussiumhq/trussium) provides the
core execution platform, including capability contracts, provider integration,
health endpoints, metrics, tracing, and structured operational logging.

### Kubernetes Operator

The [Trussium Operator](https://github.com/trussiumhq/trussium-operator)
manages `TrussiumRuntime` resources through a Kubernetes-native reconciliation
loop, including runtime configuration, deployment lifecycle, status, events,
and upgrades.

### Helm chart

The [official Helm chart](https://github.com/trussiumhq/trussium-helm)
packages the runtime for configurable Kubernetes installation, upgrade, and
operational deployment.

The chart installs the runtime workload. It does not install the Kubernetes
Operator; the Operator is a separate project for teams that want
`TrussiumRuntime` custom resources and reconciliation.

## Choose a starting point

- **Run locally:** start with the runtime [CLI](runtime/CLI.md) and
  [API usage](runtime/API_USAGE.md) guides.
- **Run privately:** follow [self-hosting](runtime/SELF_HOSTING.md), then
  review [provider configuration](runtime/PROVIDER_DEVELOPMENT.md).
- **Deploy to Kubernetes:** use the [Helm chart](helm/chart.md) for a direct
  runtime deployment, or the [Operator overview](operator/index.md) for
  reconciled custom resources.
- **Operate in production:** review [health and readiness](runtime/HEALTH.md),
  [metrics](runtime/METRICS.md), [tracing](runtime/TRACING.md), and
  [shutdown behavior](runtime/SHUTDOWN.md).

## Current release baseline

The public components are independently versioned. The current baseline is:

- [Trussium runtime v1.16.0](https://github.com/trussiumhq/trussium/releases/tag/v1.16.0)
- [Trussium Helm chart v1.0.0](https://github.com/trussiumhq/trussium-helm/releases/tag/v1.0.0)
- [Trussium Operator v1.0.0](https://github.com/trussiumhq/trussium-operator/releases/tag/v1.0.0)

The runtime, chart, and operator remain independently versioned components;
SDKs and provider adapters are optional integrations. A proposed coordinated
1.17.0 baseline is available in the runtime's
[release-candidate manifest](https://github.com/trussiumhq/trussium/blob/main/docs/RELEASE_1_17_CANDIDATE.md);
it is a review artifact and does not authorize tagging or publication.

## Project status

The public roadmap and architecture decisions describe the supported contracts
and their maturity. Start with the [runtime roadmap](runtime/ROADMAP.md), then
consult the relevant component's release and compatibility guidance before
upgrading.

## Documentation

Use the navigation to access runtime, operator, and Helm documentation. Each
section covers public contracts, deployment guidance, operational behavior,
and architecture decisions. Contributions and documentation corrections are
welcome through the [contributing guide](contributing.md).
