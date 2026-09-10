#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_PORT="${ZCOIN_HOST_PORT:-18082}"
COMPOSE=(docker compose -f "$ROOT/docker-compose.prod.yml")
log(){ printf '[zcoin] %s\n' "$*"; }
die(){ printf '[zcoin] ERROR: %s\n' "$*" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || die "docker is required"
docker compose version >/dev/null 2>&1 || die "Docker Compose v2 is required"
command -v curl >/dev/null 2>&1 || die "curl is required"
mkdir -p "$ROOT/data"
chown -R 1000:1000 "$ROOT/data" 2>/dev/null || true
if ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq "(^|:)${HOST_PORT}$"; then
  if ! "${COMPOSE[@]}" ps 2>/dev/null | grep -q "127.0.0.1:${HOST_PORT}"; then
    die "127.0.0.1:${HOST_PORT} is already used by another service"
  fi
fi
log "validating Compose"
"${COMPOSE[@]}" config >/dev/null
log "building auditor"
"${COMPOSE[@]}" build --pull auditor
log "force-recreating gateway and application on ${HOST_PORT}"
"${COMPOSE[@]}" up -d --force-recreate --remove-orphans
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${HOST_PORT}/gateway-healthz" >/dev/null 2>&1 && curl -fsS "http://127.0.0.1:${HOST_PORT}/backend-healthz" >/dev/null 2>&1; then
    log "deployment healthy"
    "${COMPOSE[@]}" ps
    printf 'Cloudflare origin: http://127.0.0.1:%s\nPublic hostname: https://zcoin.zeaz.dev\n' "$HOST_PORT"
    exit 0
  fi
  sleep 2
done
"${COMPOSE[@]}" logs --tail=200 || true
die "health checks did not pass"
