#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
build_dir=${COORD_JOB_DIR:-$(mktemp -d /tmp/hepatosim-macos.XXXXXX)}
xcodebuild -project Apps/HepatoSim.xcodeproj -scheme HepatoSim-macOS \
  -configuration Debug -destination "platform=macOS,arch=$(uname -m)" \
  -derivedDataPath "$build_dir" -jobs 2 -quiet build
app_path="$build_dir/Build/Products/Debug/HepatoSimResearch.app"
codesign --verify --deep --strict "$app_path"
printf 'Local development app (ad-hoc signed): %s\n' "$app_path"
