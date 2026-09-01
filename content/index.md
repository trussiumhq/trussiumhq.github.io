# Trussium

![Trussium logo](assets/trussium-logo.svg){ width="156" }

## Cloud-native runtime for AI applications

Trussium is a provider-neutral runtime for operating AI capabilities across
hosted providers and private models. It provides a consistent application
integration boundary while supporting cloud-native deployment, observability,
and lifecycle operations.

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

## Current release baseline

The public components are independently versioned. The current baseline is:

- [Trussium runtime v1.16.0](https://github.com/trussiumhq/trussium/releases/tag/v1.16.0)
- [Trussium Helm chart v1.0.0](https://github.com/trussiumhq/trussium-helm/releases/tag/v1.0.0)
- [Trussium Operator v1.0.0](https://github.com/trussiumhq/trussium-operator/releases/tag/v1.0.0)

The runtime and chart remain independently versioned components, and SDKs and
provider adapters are optional integrations. A proposed coordinated 1.17.0
baseline is available in the runtime's
[release-candidate manifest](https://github.com/trussiumhq/trussium/blob/main/docs/RELEASE_1_17_CANDIDATE.md);
it is a review artifact and does not authorize tagging or publication.

## Documentation

Use the navigation to access runtime, operator, and Helm documentation. Each
section covers its public contracts, deployment guidance, operational behavior,
and architecture decisions.
