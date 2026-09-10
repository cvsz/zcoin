# zCoin Production Release Checklist

## Identity

- [ ] `VERSION` matches the intended semantic version.
- [ ] `PROJECT_IDENTITY.json` contains the same version and canonical identity.
- [ ] README static version badge matches `VERSION`.
- [ ] Release tag uses `v<major>.<minor>.<patch>`.
- [ ] Canonical repository remains `cvsz/zcoin`.
- [ ] Canonical public target remains `https://coin.zeaz.dev`.

## Application quality gates

- [ ] `python -m compileall -q app tests`
- [ ] `PYTHONPATH=. pytest -q`
- [ ] `docker compose config`
- [ ] `docker compose -f docker-compose.prod.yml config`
- [ ] Docker image builds successfully.
- [ ] CI is green on the release commit.
- [ ] CodeQL is green on the release commit.
- [ ] Dependency Review is green on the release commit.
- [ ] No credentials, cookies, tokens, keys or unrevealed secrets are tracked.

## Production origin

- [ ] `127.0.0.1:18082` is free from unrelated services.
- [ ] `./deploy/deploy.sh` completes successfully.
- [ ] `/gateway-healthz` returns HTTP 200.
- [ ] `/backend-healthz` returns HTTP 200.
- [ ] `/api/version` reports the expected release version and `audit-paper-only` mode.
- [ ] SQLite data persists across container restart.

## Cloudflare cutover

- [ ] `cvsz/zworkforce` contains the reviewed `coin.zeaz.dev` DNS/Access/Tunnel configuration.
- [ ] Existing shared-tunnel routes are preserved.
- [ ] `coin.zeaz.dev` routes to `http://127.0.0.1:18082` before the catch-all 404 rule.
- [ ] Cloudflare Access policy permits only intended operators.
- [ ] Public hostname no longer returns the tunnel catch-all 404.
- [ ] Public health/application request succeeds through Cloudflare.

## Release artifact

- [ ] Push annotated or lightweight tag `v<version>` from the reviewed `main` commit.
- [ ] GitHub Release workflow succeeds.
- [ ] Release ZIP is attached.
- [ ] SHA-256 checksum is attached.
- [ ] Release badge resolves to the new tag.
- [ ] Changelog accurately describes the release.

## Scope confirmation

- [ ] No live wagering automation is present.
- [ ] No hidden-seed acquisition workflow is present.
- [ ] No account/credential automation is present.
- [ ] No authentication bypass or exploitation workflow is present.
- [ ] Documentation does not claim guaranteed future outcomes.
