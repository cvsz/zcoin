# Changelog

## 0.3.1

- Replaced repository template placeholders with the complete zCoin evidence-auditor application.
- Hardened CSV validation and symmetric result-0/result-1 edge assessment.
- Escaped HTML evidence-report inputs.
- Added non-root Docker runtime and loopback-only bindings.
- Added production Nginx gateway at `127.0.0.1:18082` to avoid zDash `18080`.
- Added idempotent deploy/verify scripts with forced gateway recreation.
- Added Cloudflare ownership/runbook documentation for `cvsz/zworkforce`.
- Expanded CI and release checks.

## 0.3.0

- Added advanced evidence validation, FDR correction, bootstrap/Bayesian analysis, holdout validation, seed-epoch replication, evidence scoring and reports.
