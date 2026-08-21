# Trussium

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

## Documentation

Use the navigation to access runtime, operator, and Helm documentation. Each
section covers its public contracts, deployment guidance, operational behavior,
and architecture decisions.
