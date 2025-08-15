#!/usr/bin/env bash
set -euo pipefail

# Clean mounted host directories defined by docker/docker-compose.yaml
# Safe by default: dry-run preview unless --yes provided.
# Options:
#   -y, --yes           Execute deletion without interactive prompt
#       --dry-run       Preview only (default)
#       --remove-dirs   Remove the directories themselves (not just contents)
#       --sudo          Force using sudo for deletions

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN=true
CONFIRM=false
REMOVE_DIRS=false
FORCE_SUDO=false

for arg in "$@"; do
  case "$arg" in
    -y|--yes) CONFIRM=true; DRY_RUN=false ;;
    --dry-run) DRY_RUN=true ;;
    --remove-dirs) REMOVE_DIRS=true ;;
    --sudo) FORCE_SUDO=true ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

# Decide sudo usage
SUDO_CMD=""
if $FORCE_SUDO; then
  SUDO_CMD="sudo"
else
  if [[ $(id -u) -ne 0 ]] && command -v sudo >/dev/null 2>&1; then
    SUDO_CMD="sudo"
  fi
fi

require_within_repo() {
  local path="$1"
  case "$path" in
    "${BASE_DIR}/"docker/*) return 0 ;;
    *)
      echo "[SKIP] Path outside repo docker/: $path" >&2
      return 1
      ;;
  esac
}

# Collected from docker/docker-compose.yaml host bind mounts
# Note: volumes/oceanbase/init.d is excluded as it contains initialization scripts
mapfile -t PATHS < <(cat <<'EOF'
${BASE_DIR}/docker/volumes/app/storage
${BASE_DIR}/docker/volumes/db/data
${BASE_DIR}/docker/volumes/redis/data
${BASE_DIR}/docker/volumes/sandbox/dependencies
${BASE_DIR}/docker/volumes/sandbox/conf
${BASE_DIR}/docker/volumes/plugin_daemon
${BASE_DIR}/docker/volumes/weaviate
${BASE_DIR}/docker/volumes/qdrant
${BASE_DIR}/docker/volumes/couchbase/data
${BASE_DIR}/docker/volumes/pgvector/data
${BASE_DIR}/docker/volumes/pgvecto_rs/data
${BASE_DIR}/docker/volumes/chroma
${BASE_DIR}/docker/volumes/oceanbase/data
${BASE_DIR}/docker/volumes/oceanbase/conf
${BASE_DIR}/docker/volumes/certbot/conf
${BASE_DIR}/docker/volumes/certbot/www
${BASE_DIR}/docker/volumes/certbot/logs
${BASE_DIR}/docker/volumes/opensearch/data
${BASE_DIR}/docker/volumes/milvus/etcd
${BASE_DIR}/docker/volumes/milvus/minio
${BASE_DIR}/docker/volumes/milvus/milvus
${BASE_DIR}/docker/nginx/ssl
${BASE_DIR}/docker/vastbase/lic
${BASE_DIR}/docker/vastbase/data
${BASE_DIR}/docker/vastbase/backup
${BASE_DIR}/docker/vastbase/backup_log
EOF
)

echo "Repo base: ${BASE_DIR}"
echo "Mode: $( $DRY_RUN && echo DRY-RUN || echo EXECUTE ) | remove-dirs: ${REMOVE_DIRS} | sudo: $( [[ -n $SUDO_CMD ]] && echo on || echo off )"
echo

if ! $CONFIRM && ! $DRY_RUN; then
  read -r -p "This will delete data under mounted directories. Continue? [y/N] " ans
  case "${ans:-}" in
    y|Y) ;;
    *) echo "Aborted."; exit 1 ;;
  esac
fi

for p in "${PATHS[@]}"; do
  # expand ${BASE_DIR} in heredoc entries
  p=$(eval echo "$p")
  require_within_repo "$p" || continue
  if [[ -d "$p" ]]; then
    if $DRY_RUN; then
      if $REMOVE_DIRS; then
        echo "[DRY] rm -rf -- $p"
      else
        echo "[DRY] rm -rf -- $p/* $p/.[!.]* $p/..?* (ignore missing)"
      fi
    else
      if $REMOVE_DIRS; then
        $SUDO_CMD rm -rf -- "$p"
        echo "[OK] removed dir $p"
      else
        # remove contents but keep the directory
        $SUDO_CMD rm -rf -- "$p"/* "$p"/.[!.]* "$p"/..?* 2>/dev/null || true
        echo "[OK] cleaned contents of $p"
      fi
    fi
  else
    echo "[SKIP] not found: $p"
  fi
done

echo "Done."


