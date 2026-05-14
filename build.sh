#!/bin/bash
set -euo pipefail

APP_ID="sh.ppy.osu"
MANIFEST="${APP_ID}.yaml"
BUILD_DIR="build-dir"

echo "Building and installing ${APP_ID}..."

# Build the flatpak and install it for the current user
flatpak run org.flatpak.Builder --user --install --force-clean "${BUILD_DIR}" "${MANIFEST}"

echo "Build and installation complete."
echo "You can run the app with: flatpak run ${APP_ID}"
