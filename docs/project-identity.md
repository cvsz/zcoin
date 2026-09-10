# zCoin Project Identity Specification

## Canonical identity

**zCoin — CoinFlip Evidence Auditor** is the canonical product name. The stable machine identifier is `dev.zeaz.zcoin`, the source repository is `cvsz/zcoin`, and the canonical public application hostname is `coin.zeaz.dev`.

The project belongs to the ZeaZDev product family and is maintained under the public GitHub owner `cvsz`.

## Identity contract

| Attribute | Canonical value |
|---|---|
| Product name | `zCoin` |
| Display name | `zCoin — CoinFlip Evidence Auditor` |
| Project ID | `dev.zeaz.zcoin` |
| Repository | `https://github.com/cvsz/zcoin` |
| Product family | `ZeaZDev` |
| Public hostname | `coin.zeaz.dev` |
| API/runtime version | `0.3.1` |
| Release tag | `v0.3.1` |
| Release channel | `stable` |
| License | `MIT` |
| Application mode | `audit-research-paper-only` |

`PROJECT_IDENTITY.json` is the machine-readable form of this contract. `VERSION` is the source version for application and release packaging.

## Product promise

zCoin is designed to answer one question rigorously: **does the available historical evidence support a reproducible integrity or statistical finding, or is the observed pattern consistent with random variation?**

The project therefore prioritizes cryptographic verification, reproducibility, statistical controls, independent holdout validation, cross-seed-epoch replication, and explicit uncertainty over pattern chasing.

## Scope boundary

Supported scope includes historical revealed-seed verification, commitment verification, nonce/sequence auditing, statistical analysis, evidence scoring, simulation and reporting.

Excluded scope includes live wagering automation, credential automation, hidden or unrevealed secret acquisition, authentication bypass, third-party exploitation, and guarantees about future outcomes.

## Runtime identity

```text
Public target       https://coin.zeaz.dev
Cloudflare edge     cvsz/zworkforce
Production origin   http://127.0.0.1:18082
Gateway             Nginx
Application          FastAPI / Python 3.12+
Internal app port    8000
Persistence          SQLite
Container runtime    Docker
```

The public hostname is separated from the application repository on purpose. `cvsz/zcoin` owns application behavior and the loopback gateway. `cvsz/zworkforce` owns Cloudflare DNS, Access and shared tunnel infrastructure.

## Release identity

A software release uses semantic versioning and the `v<major>.<minor>.<patch>` Git tag convention. The release workflow must run tests, compile checks and a Docker build before producing the distributable ZIP and SHA-256 checksum.

The README release badge is backed by GitHub Releases. CI, CodeQL and Dependency Review badges are backed directly by their GitHub Actions workflows so the displayed state tracks the current `main` branch.

## Badge policy

The primary README badge row communicates four different classes of state:

1. **Release identity** — latest GitHub Release and current source version.
2. **Quality gates** — CI, CodeQL and Dependency Review.
3. **Runtime identity** — Python, FastAPI and Docker.
4. **Governance/deployment** — MIT license, audit-only scope and canonical production target.

Badges must not imply that the public hostname is healthy merely because application CI is green. Application release readiness and production cutover are separate states.

## Release maturity

`v0.3.1` is the first release line with the complete evidence-auditor identity, hardened Docker packaging, production loopback gateway, statistical validation stack, security quality gates and reproducible release artifact workflow.

Production availability at `coin.zeaz.dev` additionally requires the corresponding Cloudflare infrastructure to be active in `cvsz/zworkforce`.
