# zCoin brand assets

This document defines the repository artwork shipped with **zCoin — CoinFlip Evidence Auditor**.

## Official repository banner

**Path:** `docs/assets/zcoin-banner.jpg`  
**Dimensions:** 1280 × 480 px  
**Purpose:** README hero, project landing pages, release notes, documentation headers and repository announcements.

The banner communicates the complete product identity in one visual system: zCoin as an evidence-first CoinFlip auditor, the cryptographic verification layer, statistical analysis dashboard, evidence reporting capabilities, release/security status and production architecture. The visual language is intentionally technical rather than promotional: dark infrastructure-oriented styling, blue verification/data accents, restrained gold for the coin/evidence motif, and explicit research-only context.

### Recommended alt text

> zCoin — CoinFlip Evidence Auditor project banner showing cryptographic verification, statistical analysis, evidence reporting, release status and the Cloudflare-to-Nginx-to-FastAPI production architecture.

## GitHub social preview

**Path:** `docs/assets/zcoin-social-preview.jpg`  
**Dimensions:** 1280 × 640 px  
**Purpose:** GitHub repository social preview / Open Graph artwork.

The social-preview version preserves the same artwork inside GitHub's preferred 2:1 presentation canvas. It is intended for **Settings → General → Social preview** when repository administration access is available.

## Identity represented by the artwork

| Field | Value |
|---|---|
| Product | zCoin |
| Full name | zCoin — CoinFlip Evidence Auditor |
| Project ID | `dev.zeaz.zcoin` |
| Product family | ZeaZDev |
| Repository | `cvsz/zcoin` |
| Release line | `v0.3.x` |
| Public target | `coin.zeaz.dev` |
| Runtime | Python 3.12 + FastAPI |
| Deployment | Docker + Nginx |
| Edge | Cloudflare Access + Tunnel |
| Persistence | SQLite evidence store |
| Scope | audit / research / paper-only |

## Core narrative

The visual hierarchy should reinforce the project mission:

1. **Verify** — reproduce historical outcomes from revealed seeds and validate server-seed commitments.
2. **Analyze** — measure distributions, independence, autocorrelation, change points and uncertainty.
3. **Validate** — apply multiple-testing correction, holdout testing and cross-seed-epoch replication.
4. **Report** — produce reproducible JSON/HTML evidence reports and deterministic dataset fingerprints.
5. **Operate securely** — run behind a loopback-only Nginx origin, Cloudflare Access/Tunnel and CI/security gates.

The artwork must not imply guaranteed wins, future-outcome prediction, hidden-seed recovery, credential automation or live wagering automation.

## Visual direction

- **Base:** near-black / deep navy infrastructure background.
- **Primary accent:** electric blue for verification, data and API concepts.
- **Secondary accent:** restrained gold for the evidence/coin motif.
- **Status accent:** green only for verified/passing states.
- **Typography:** clean geometric or system sans-serif; high contrast and readable at repository-card scale.
- **Iconography:** cryptographic verification, charts, reports, API, containers, gateway, cloud edge and evidence storage.
- **Tone:** technical, trustworthy, measurable, reproducible and research-driven.

## Usage rules

- Keep the banner proportional; do not stretch it non-uniformly.
- Keep the complete product title visible when used as the primary hero asset.
- Do not remove research/audit context when using the image in gambling-adjacent environments.
- Do not overlay claims such as "guaranteed win", "predict next flip" or similar statements.
- Prefer the 1280×480 asset inside README/documentation and the 1280×640 asset for social preview.
- Keep generated derivatives in `docs/assets/` and document them here.
- Update release/version text in future artwork when the major visual is regenerated for a new release line.

## Repository integration

The README references the banner using a repository-relative path:

```html
<img src="docs/assets/zcoin-banner.jpg" alt="zCoin — CoinFlip Evidence Auditor ..." width="100%">
```

This keeps the README self-contained and avoids third-party image hosting.

## Source-of-truth boundaries

Artwork and application identity are owned by `cvsz/zcoin`. DNS, Cloudflare Access and shared-tunnel infrastructure remain owned by `cvsz/zworkforce`; the banner illustrates that boundary but does not redefine infrastructure ownership.
