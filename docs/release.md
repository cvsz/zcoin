# Release

1. Run `make release-check`.
2. Build with `docker compose -f docker-compose.prod.yml build`.
3. Verify `./deploy/deploy.sh` on the target host.
4. Tag `vX.Y.Z` only after CI passes.
5. Release workflow creates a ZIP and SHA-256 checksum.
6. Cloudflare changes are reviewed and applied separately in `cvsz/zworkforce`.
