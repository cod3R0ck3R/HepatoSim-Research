#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${COORD_JOB_DIR:?Run through the shared coordinator, or set COORD_JOB_DIR to a new build directory}"
build_dir="$COORD_JOB_DIR/ReleaseBuild"
archive_dir="$COORD_JOB_DIR/release-assets"
mkdir "$archive_dir"
xcodebuild -project Apps/HepatoSim.xcodeproj -scheme HepatoSim-macOS \
  -configuration Release -destination "platform=macOS,arch=arm64" \
  -derivedDataPath "$build_dir" -jobs 2 -quiet \
  CODE_SIGN_IDENTITY=- CODE_SIGN_STYLE=Manual DEVELOPMENT_TEAM= \
  MARKETING_VERSION=0.1.0 CURRENT_PROJECT_VERSION=1 build
app="$build_dir/Build/Products/Release/HepatoSimResearch.app"
/usr/bin/strip -S -x "$app/Contents/MacOS/HepatoSimResearch"
codesign --force --sign - --options runtime --entitlements Apps/macOS.entitlements "$app"
codesign --verify --deep --strict "$app"
/usr/bin/plutil -lint "$app/Contents/Info.plist"
archs=$(/usr/bin/lipo -archs "$app/Contents/MacOS/HepatoSimResearch")
case "$archs" in "x86_64 arm64"|"arm64 x86_64") ;; *) exit 1 ;; esac
staging="$build_dir/LicensedPackage"
mkdir "$staging"
/usr/bin/ditto "$app" "$staging/HepatoSimResearch.app"
cp LICENSE THIRD_PARTY_NOTICES.md "$staging/"
/usr/bin/ditto -c -k --sequesterRsrc "$staging" "$archive_dir/HepatoSim-Research-0.1.0-alpha.1-macOS-universal.zip"
cd "$archive_dir"
/usr/bin/shasum -a 256 HepatoSim-Research-0.1.0-alpha.1-macOS-universal.zip > SHA256SUMS.txt
printf 'Ad-hoc signed research prerelease, not notarized: %s\n' "$archive_dir"
