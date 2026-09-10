# About zCoin

**zCoin — CoinFlip Evidence Auditor** is a ZeaZDev project maintained in `cvsz/zcoin` for reproducible historical outcome verification, statistical evidence analysis, and paper-only simulation.

## Identity

- **Product:** zCoin
- **Full name:** zCoin — CoinFlip Evidence Auditor
- **Project ID:** `dev.zeaz.zcoin`
- **Repository:** `https://github.com/cvsz/zcoin`
- **Owner:** `cvsz`
- **Product family:** ZeaZDev
- **Canonical application URL:** `https://zcoin.zeaz.dev`
- **Current version:** `0.3.1`
- **Release channel:** stable
- **License:** MIT
- **Primary runtime:** Python 3.12 / FastAPI
- **Production gateway:** Nginx on `127.0.0.1:18082`
- **Edge boundary:** Cloudflare Access + Tunnel managed by `cvsz/zworkforce`

## Mission

zCoin exists to replace guesswork with reproducible evidence. It verifies historical revealed-seed CoinFlip results, checks seed commitments and sequence integrity, measures distributional and serial anomalies, applies multiple-testing correction and out-of-sample validation, and produces evidence reports that distinguish random variation from stronger implementation or statistical signals.

## Core capabilities

- HMAC-SHA256 outcome reproduction for supported historical verifier mappings
- SHA-256 server-seed commitment verification
- nonce and sequence-integrity auditing
- idempotent dataset ingestion and deterministic evidence fingerprints
- proportion, runs, streak, autocorrelation, transition and change-point analysis
- Bootstrap and Bayesian inference around break-even probability
- Benjamini-Hochberg false-discovery-rate correction
- chronological train/holdout validation
- seed-epoch segmentation and replication checks
- conservative evidence scoring and classification
- paper-only strategy comparison, walk-forward analysis and Monte Carlo null simulation
- JSON and printable HTML evidence reports
- Dockerized local/production runtime with CI, CodeQL and dependency-review gates

## Security and scope

zCoin is intentionally an **audit/research/paper-only** system. It does not contain live wagering automation, credential automation, hidden-seed acquisition, authentication bypass, exploitation workflows, or guaranteed-win logic.

Only historical data that the operator is authorized to use should be ingested. Revealed server seeds may be used for retrospective verification. Passwords, cookies, access tokens, private account material and unrevealed secrets must not be committed or uploaded as datasets.

## Release identity

The authoritative human-readable project identity is documented in `docs/project-identity.md`. The machine-readable contract is `PROJECT_IDENTITY.json`. The repository `VERSION` file remains the canonical source version used for release packaging.

A GitHub release is produced from a `v*` tag only after automated test, Docker, dependency and security gates pass.
