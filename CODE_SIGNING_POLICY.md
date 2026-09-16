# Code signing policy

This policy defines how official Windows release artifacts for **有岐 / video-editing-agent** are eligible for production code signing.

## SignPath Foundation

Upon acceptance of this project's SignPath Foundation application, production Windows release signing will use:

> **Free code signing provided by SignPath.io, certificate by SignPath Foundation**

Until that application is approved and the trusted build integration is active, no project artifact is represented as SignPath-signed. The existing `v1.0.0` release predates this policy and is not covered by a SignPath Foundation signature.

Source repository: <https://github.com/orange-lee-tech/video-editing-agent>

Privacy policy: [PRIVACY.md](PRIVACY.md)

## Team roles

The public GitHub identities below are the code-signing team. These operational roles do not change copyright ownership or contributor attribution.

### Authors / committers

- [`orange-lee-tech`](https://github.com/orange-lee-tech)
- [`liulei123366`](https://github.com/liulei123366)

These members are trusted maintainers of the source repository and release/build scripts.

### Reviewers

- [`orange-lee-tech`](https://github.com/orange-lee-tech)
- [`liulei123366`](https://github.com/liulei123366)

Changes proposed by non-committers must receive human review before they are accepted. Release-affecting changes, including build, packaging, update, signing, and release workflow changes, must be reviewed before they are eligible for production release signing.

### Approvers

- [`orange-lee-tech`](https://github.com/orange-lee-tech)
- [`liulei123366`](https://github.com/liulei123366)

Every production signing request requires at least one explicit human approval in SignPath. CI credentials are submitters only and are not treated as human approval.

## Multi-factor authentication

Every human member of the code-signing team must have multi-factor authentication enabled for both GitHub and SignPath before production SignPath signing is activated. A member who does not meet this requirement must not act as an Author, Reviewer, or Approver for the signing process.

## Trusted build and origin

Official SignPath signing requests must satisfy all of the following:

1. the artifact is built by repository-controlled GitHub Actions configuration from this repository;
2. all jobs leading to the signing request run on GitHub-hosted runners unless SignPath explicitly approves another trusted runner configuration;
3. the unsigned artifact is uploaded to GitHub Actions before submission to SignPath;
4. submission uses the official SignPath GitHub integration and SignPath trusted-build/origin verification;
5. source revision, build job, product version, and artifact identity remain traceable in the release evidence;
6. production signing is performed only after the relevant automated quality gates pass and a human signing approval is granted;
7. locally built or manually modified binaries are not eligible for routine production signing.

Release-signing branch/tag restrictions and trusted-build settings are enforced in SignPath as part of the production signing policy.

## What may be signed

The project certificate is used only for binaries built from project-maintained source and build scripts.

Project-built Windows executables and the project installer may be signed. Upstream third-party binaries that are merely bundled with the application are not re-signed as if they were project-owned binaries. Third-party software remains governed by its own licenses and provenance records.

The project maintains the bundled-runtime inventory and licensing evidence in:

- `resources/packaging/runtime-manifest.json`;
- `resources/licenses/THIRD_PARTY_RUNTIME_NOTICES.md`;
- `LICENSES/` and the dependency/upstream governance documents.

## Artifact metadata

Production artifact configuration must enforce consistent release metadata, including:

- product name: **有岐** / **Youqi** where the artifact format requires an English-compatible value;
- one application version across the artifacts produced for the same release;
- a source revision that corresponds to the verified GitHub build origin.

## Privacy and network services

有岐 is local-first. User media and projects remain local unless the user selects or configures functionality that requires an external provider. The application does not bundle provider credentials.

Optional external AI/API providers and the public update channel are documented in [PRIVACY.md](PRIVACY.md). Users control whether to configure and invoke third-party AI providers. Update checks retrieve public version metadata and do not upload user media or project files.

## Release and incident rules

- Every production signing request is manually approved.
- A signed artifact must not be modified after signing.
- A release whose provenance, integrity, or signing authorization cannot be established must not be published as an official signed release.
- Suspected key, workflow, repository, or release compromise must halt production signing until investigated.
- If a signed release is found to violate this policy, the maintainers will cooperate with SignPath Foundation on investigation, containment, and certificate/signature remediation as required.

This policy is version-controlled with the source repository. Material changes to the signing boundary, signing roles, trusted build path, or release approval process require review before they take effect.