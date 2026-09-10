#!/usr/bin/env bash
set -Eeuo pipefail
HOST_PORT="${ZCOIN_HOST_PORT:-18082}"
PUBLIC_URL="${ZCOIN_PUBLIC_URL:-https://coin.zeaz.dev}"
printf '%-24s' 'gateway health: '; curl -fsS "http://127.0.0.1:${HOST_PORT}/gateway-healthz"; echo
printf '%-24s' 'backend health: '; curl -fsS "http://127.0.0.1:${HOST_PORT}/backend-healthz"; echo
printf '%-24s' 'API version: '; curl -fsS "http://127.0.0.1:${HOST_PORT}/api/version"; echo
printf '%-24s' 'public HTTP status: '; curl -sS -o /dev/null -w '%{http_code}\n' "$PUBLIC_URL/"
