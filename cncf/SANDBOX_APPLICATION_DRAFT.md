# CNCF Sandbox Application Draft: Trussium

> This is a working draft for the CNCF Sandbox issue form. Do not submit it
> until the linked governance documents are merged and the maintainer confirms
> the final application content.

## Basic project information

**Project summary**

Trussium is a provider-neutral, cloud-native runtime for operating AI
capabilities across hosted providers and private models.

**Project description**

Trussium provides an application integration boundary for AI capabilities,
allowing applications to work across hosted providers and private models without
being coupled to provider-specific SDKs. The project includes a Python runtime,
a Kubernetes Operator for declarative lifecycle management, and an official Helm
chart for Kubernetes deployment. Its public contracts cover capability execution,
health and readiness, metrics, tracing, structured operational logging, runtime
configuration, reconciliation, and upgrade behavior. Trussium is designed as a
reusable open-source project for organizations operating AI workloads in
cloud-native environments.

**Project type**

Reusable open-source project, not a reference architecture or implementation.

**Project organization**

<https://github.com/trussiumhq>

**Repositories in scope**

- <https://github.com/trussiumhq/trussium>
- <https://github.com/trussiumhq/trussium-operator>
- <https://github.com/trussiumhq/trussium-helm>
- <https://github.com/trussiumhq/trussiumhq.github.io>

## Project policies

- Website: <https://trussiumhq.github.io>
- Contributing guide: <https://github.com/trussiumhq/trussiumhq.github.io/blob/main/CONTRIBUTING.md>
- Code of Conduct: <https://github.com/trussiumhq/trussiumhq.github.io/blob/main/CODE_OF_CONDUCT.md>
- Governance: <https://github.com/trussiumhq/trussiumhq.github.io/blob/main/GOVERNANCE.md>
- Maintainers: <https://github.com/trussiumhq/trussiumhq.github.io/blob/main/MAINTAINERS.md>
- Security policy: <https://github.com/trussiumhq/trussiumhq.github.io/blob/main/SECURITY.md>

## License

The repositories in scope are licensed under Apache License 2.0.

## Standards or specifications

N/A. Trussium is a software project and does not define a formal standard or
specification.

## Business product or service separation

Trussium is the vendor-neutral open-source upstream project. A future hosted
platform will be a separate commercial offering and will not restrict
Trussium’s open-source licensing, governance, contribution process, or public
roadmap.

## Adopters

No adopters are publicly listed at this time.

## Submission checklist

- [ ] Confirm all policy links resolve on the default branch.
- [ ] Confirm the project description and business-separation statement.
- [ ] Complete any remaining CNCF Sandbox issue-form fields at submission time.
- [ ] Submit through <https://github.com/cncf/sandbox/issues/new/choose>.
