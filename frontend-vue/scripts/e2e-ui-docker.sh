#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found"
  exit 1
fi

IMAGE="${PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright:v1.57.0-jammy}"

docker run --rm -t \
  -v "${ROOT_DIR}:/work" \
  -w /work \
  "${IMAGE}" \
  bash -lc 'corepack enable && pnpm install --frozen-lockfile || pnpm install --no-frozen-lockfile && pnpm run e2e:ui'

