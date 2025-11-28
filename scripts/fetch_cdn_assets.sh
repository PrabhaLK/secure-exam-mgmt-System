#!/usr/bin/env bash
set -euo pipefail

# Script to download CDN assets into static/vendor/
# Run from project root: bash scripts/fetch_cdn_assets.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATIC_DIR="$ROOT_DIR/static/vendor"
mkdir -p "$STATIC_DIR/jquery"
mkdir -p "$STATIC_DIR/bootstrap/dist/css"
mkdir -p "$STATIC_DIR/bootstrap/dist/js"
mkdir -p "$STATIC_DIR/popper.js/dist/umd"
mkdir -p "$STATIC_DIR/buttons"

echo "Downloading jQuery..."
curl -sS -L -o "$STATIC_DIR/jquery/jquery.min.js" "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"

echo "Downloading Bootstrap CSS..."
curl -sS -L -o "$STATIC_DIR/bootstrap/dist/css/bootstrap.min.css" "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"

echo "Downloading Bootstrap JS..."
curl -sS -L -o "$STATIC_DIR/bootstrap/dist/js/bootstrap.min.js" "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"

echo "Downloading Popper..."
curl -sS -L -o "$STATIC_DIR/popper.js/dist/umd/popper.min.js" "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"

echo "Downloading GitHub buttons script..."
curl -sS -L -o "$STATIC_DIR/buttons/buttons.js" "https://buttons.github.io/buttons.js"

cat > "$ROOT_DIR/README_FETCH_ASSETS.md" <<'EOF'
Run `bash scripts/fetch_cdn_assets.sh` to populate `static/vendor/` with local copies of the CDN files referenced in templates.
After running, commit the files in `static/vendor/` to your repo (or add them to your deployment pipeline).
EOF

echo "Done. Read README_FETCH_ASSETS.md for next steps."
