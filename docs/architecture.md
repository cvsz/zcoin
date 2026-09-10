# Architecture

```text
Historical CSV
    |
    v
FastAPI ingest ----> SQLite
    |
    +--> seed commitment verification
    +--> HMAC result reproduction
    +--> nonce integrity
    +--> statistical validation
    +--> seed-epoch / holdout replication
    +--> paper-only simulation
    |
    v
JSON / HTML evidence report

Internet
    |
Cloudflare Access + Tunnel   [cvsz/zworkforce]
    |
127.0.0.1:18082
    |
Nginx gateway                [cvsz/zcoin]
    |
Docker internal network
    |
FastAPI :8000
```

The application never needs a casino login. Full cryptographic verification uses server seeds only after reveal. The production origin is loopback-only.
