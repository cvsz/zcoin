# Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test
make run
```

Tests cover verifier vectors, ingest idempotency, evidence integrity gating, statistical helpers, report escaping and paper-only strategy behavior.
