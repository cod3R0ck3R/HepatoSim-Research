#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Temporary build paths avoid Finder metadata in cloud-managed Documents folders.
verification_dir=${COORD_JOB_DIR:-$(mktemp -d /tmp/hepatosim-verify.XXXXXX)}
swift test --jobs 2 --scratch-path "$verification_dir/package"
swift run --jobs 2 --scratch-path "$verification_dir/package" hepatosim "$verification_dir/synthetic-run"
printf 'Verification artifacts: %s\n' "$verification_dir"
