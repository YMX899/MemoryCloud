#!/usr/bin/env bash
set -euo pipefail

URL="${MEMORYCLOUD_HEALTH_URL:-http://127.0.0.1:18085/health}"
SERVICE="${MEMORYCLOUD_SERVICE:-demo-memory-project.service}"
LOG_DIR="${MEMORYCLOUD_HEALTH_LOG_DIR:-.memorycloud-data/logs}"
LOG_FILE="$LOG_DIR/health-watchdog.log"

mkdir -p "$LOG_DIR"

for attempt in 1 2 3 4 5; do
  if curl -fsS --max-time 5 "$URL" >/dev/null; then
    exit 0
  fi
  sleep 3
done

{
  printf '%s health check failed for %s; restarting %s\n' "$(date -Is)" "$URL" "$SERVICE"
  systemctl restart "$SERVICE"
  sleep 3
  systemctl is-active "$SERVICE" || true
} >>"$LOG_FILE" 2>&1
