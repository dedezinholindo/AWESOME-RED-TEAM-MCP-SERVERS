#!/usr/bin/env bash
# This script sets up the mcp-for-security project by installing dependencies,
# building Node.js MCP servers, and generating the mcp.config.json configuration file.

set -euo pipefail

# === Configuration Variables ===
PROJECT_BASE="${1:-$HOME/mcp-project/}"
REPO_URL="https://github.com/cyproxio/mcp-for-security.git"
CONFIG_FILE="$PROJECT_BASE/mcp-for-security/mcp.config.json"
# ================================

echo "[*] Updating package lists and installing required packages..."
sudo apt update -qq
sudo apt -y install git curl jq build-essential > /dev/null

# Check if Node.js is installed; if not, install it via NodeSource
if ! command -v node >/dev/null; then
  echo "[*] Node.js not found. Installing via NodeSource..."
  curl -fsSL https://deb.nodesource.com/setup_current.x | sudo -E bash -
  sudo apt -y install nodejs > /dev/null
fi

echo "[*] Cloning or updating the mcp-for-security repository..."
mkdir -p "$PROJECT_BASE"
cd "$PROJECT_BASE"
if [ -d "mcp-for-security" ]; then
  git -C mcp-for-security pull --quiet
else
  git clone --depth 1 "$REPO_URL"
fi

echo "[*] Building Node.js MCP servers..."
cd mcp-for-security
for dir in *-mcp; do
  echo "    • Building $dir"
  pushd "$dir" > /dev/null
  if [ -f package-lock.json ]; then
    npm ci --silent
  else
    npm install --silent
  fi
  npm run build --silent
  popd > /dev/null
done

echo "[*] Generating mcp.config.json..."
TOOLS=$(find . -maxdepth 1 -type d -name '*-mcp' -printf '%f\n' | sed 's/-mcp//' | tr '\n' ' ')

jq -n \
  --arg base "$PROJECT_BASE/mcp-for-security" \
  --arg tools "$TOOLS" '
  reduce ($tools | split(" "))[] as $t ({}; . + {
      ($t): {
        command: "node",
        args: [($base + "/" + $t + "-mcp/build/index.js"), $t]
      }
    }
  )
  | {mcpServers: .}
' > "$CONFIG_FILE"

echo "[✓] Configuration file created at: $CONFIG_FILE"
