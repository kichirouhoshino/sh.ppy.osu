#!/bin/bash
set -euo pipefail

# Get latest release JSON from GitHub API
echo "Fetching latest release info from GitHub..."
release_json=$(curl -L -s https://api.github.com/repos/ppy/osu/releases/latest)

latest_version=$(echo "$release_json" | jq -r '.tag_name')
published_at=$(echo "$release_json" | jq -r '.published_at')
release_date=$(echo "$published_at" | cut -d'T' -f1)

# Get current version from YAML
current_version=$(grep -o "download/[^\"].*/osu.AppImage" sh.ppy.osu.yaml | sed 's/^download\///;s/\/osu.AppImage//')

echo "Current version: $current_version"
echo "Latest version:  $latest_version"
echo "Release date:    $release_date"

if [ "$current_version" = "$latest_version" ]; then
    echo "There is no new version."
    exit 0
fi

# Find download URL for osu.AppImage
download_url=$(echo "$release_json" | jq -r '.assets[] | select(.name == "osu.AppImage") | .browser_download_url')

if [ -z "$download_url" ] || [ "$download_url" = "null" ]; then
    echo "Error: Could not find osu.AppImage download URL"
    exit 1
fi

echo "Updating osu! to version $latest_version..."

# Download and compute sha256
echo "Downloading AppImage to compute SHA256..."
curl -L --progress-bar -o osu.AppImage.tmp "$download_url"
sha256sum=$(sha256sum osu.AppImage.tmp | cut -d " " -f 1)
rm -f osu.AppImage.tmp

echo "New SHA256: $sha256sum"

# Update YAML using Python for safety and precision
python3 -c "
import re
with open('sh.ppy.osu.yaml', 'r') as f:
    content = f.read()

# Replace URL
content = content.replace('/download/$current_version/osu.AppImage', '/download/$latest_version/osu.AppImage')

# Replace sha256 specifically following that URL
pattern = r'(url:\s*https://github\.com/ppy/osu/releases/download/$latest_version/osu\.AppImage\n\s*sha256:\s*)[a-f0-9]+'
content = re.sub(pattern, r'\g<1>$sha256sum', content)

with open('sh.ppy.osu.yaml', 'w') as f:
    f.write(content)
"

# Update XML appdata
if ! grep -q "version=\"$latest_version\"" sh.ppy.osu.appdata.xml; then
    # Insert new release line inside <releases>
    sed -i "/<releases>/a \ \ \ \ \ \ \ \ <release version=\"$latest_version\" date=\"$release_date\"\/>" sh.ppy.osu.appdata.xml
    echo "Updated sh.ppy.osu.appdata.xml with the new release."
fi

echo "Update complete."
