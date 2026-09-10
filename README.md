# zCoin — CoinFlip Evidence Auditor

`zCoin` is an offline-first audit stack for verifying revealed-seed CoinFlip history and testing whether an apparent statistical edge survives integrity checks, multiple-testing correction, holdout validation, seed-epoch replication, and Monte Carlo baselines.

**Public target:** `https://coin.zeaz.dev`  
**Production origin:** `http://127.0.0.1:18082`  
**Version:** `0.3.1`

> Verification, research, and paper simulation only. This repository does not place live bets, obtain hidden server seeds, bypass authentication, or claim guaranteed wins.

## Features

- old/new HMAC-SHA256 CoinFlip verifier mappings
- SHA-256 revealed server-seed commitment checks
- idempotent CSV ingestion with SQLite persistence
- nonce duplicate/gap/order auditing
- proportion, runs, streak, autocorrelation and transition analysis
- bootstrap 99% confidence intervals
- Bayesian posterior probability above economic break-even
- change-point signals and chronological train/holdout validation
- seed-epoch segmentation and Benjamini-Hochberg FDR correction
- conservative evidence scoring and classification
- paper-only strategy comparison, walk-forward simulation and Monte Carlo null models
- JSON evidence bundles and printable HTML reports
- FastAPI dashboard/API
- non-root Docker runtime
- loopback-only production Nginx gateway on `18082`
- CI, CodeQL, dependency review, release ZIP + SHA-256

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Docker development:

```bash
docker compose up --build -d
curl http://127.0.0.1:8000/healthz
```

Production origin:

```bash
./deploy/deploy.sh
./deploy/verify.sh
```

## Cloudflare ownership boundary

`zcoin` owns the application and loopback gateway. `cvsz/zworkforce` owns DNS, Cloudflare Access and the shared tunnel. Intended mapping:

```text
coin.zeaz.dev -> Cloudflare Access -> existing tunnel -> 127.0.0.1:18082 -> Nginx -> auditor:8000
```

Do not reuse `18080`; it belongs to zDash. See `docs/cloudflare.md` before changing tunnel state.

## CSV input

Minimum:

```csv
client_seed,nonce,reported_result
client-a,1001,0
client-a,1002,1
```

Full audit history after server-seed reveal:

```csv
ts,bet_id,server_seed,server_seed_hash,client_seed,nonce,round,reported_result,amount,payout_multiplier
2026-09-10T10:00:00Z,b1,REVEALED_SEED,SHA256_COMMITMENT,CLIENT,1001,1,0,1,1.98
```

Never put passwords, cookies, access tokens, account credentials, or unrevealed secrets in datasets.

## API

```text
GET    /healthz
GET    /api/version
POST   /api/verify
POST   /api/ingest
GET    /api/datasets
GET    /api/analysis/{dataset}
GET    /api/advanced/{dataset}
GET    /api/evidence/{dataset}
DELETE /api/datasets/{dataset}
GET    /api/paper/compare/{dataset}
GET    /api/paper/walk-forward/{dataset}
GET    /api/paper/monte-carlo/{dataset}
GET    /report/{dataset}
```

The strongest evidence classification requires complete cryptographic result coverage and independent replication. A historical anomaly is not a prediction of the next flip.
