#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_PORT="${ZCOIN_HOST_PORT:-18082}"
COMPOSE=(docker compose -f "$ROOT/docker-compose.prod.yml")
log(){ printf '[zcoin] %s\n' "$*"; }
die(){ printf '[zcoin] ERROR: %s\n' "$*" >&2; exit 1; }

log "checking for running zcoin containers"
"${COMPOSE[@]}" ps --format '{{.Names}} {{.Status}}' | grep -q zcoin || log "no zcoin containers running"

log "stopping and removing zcoin containers"
"${COMPOSE[@]}" down --rmi local --volumes 2>/dev/null || true

log "verifying port ${HOST_PORT} is free"
if ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq "(^|:)${HOST_PORT}$"; then
  log "WARNING: port ${HOST_PORT} is still in use"
fi

log "rollback complete"
log "To redeploy: bash deploy/deploy.sh"
