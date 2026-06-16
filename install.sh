#!/usr/bin/env bash
# Prompt Optimizer — one-line installer for macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/tanmayagr2021/prompt-optimizer/main/install.sh | bash

set -e

REPO="https://github.com/tanmayagr2021/prompt-optimizer"
RAW="https://raw.githubusercontent.com/tanmayagr2021/prompt-optimizer/main"
INSTALL_DIR="$HOME/Documents/prompt-optimizer"
APP_DEST="$HOME/Desktop/PromptOptimizer.app"

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

info()    { echo -e "${BOLD}${GREEN}✔ $1${RESET}"; }
warn()    { echo -e "${YELLOW}⚠ $1${RESET}"; }
step()    { echo -e "\n${BOLD}▸ $1${RESET}"; }
fail()    { echo -e "${RED}✖ $1${RESET}"; exit 1; }

echo ""
echo -e "${BOLD}⚡ Prompt Optimizer — Installer${RESET}"
echo "────────────────────────────────"

# ── 1. Python 3 ──────────────────────────────────────────────────────────────
step "Checking Python 3..."
if ! command -v python3 &>/dev/null; then
    fail "Python 3 not found. Install it from https://www.python.org/downloads/ then re-run this script."
fi
PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
info "Python $PY_VER found"

# ── 2. pip ───────────────────────────────────────────────────────────────────
step "Checking pip..."
if ! python3 -m pip --version &>/dev/null; then
    warn "pip not found — installing..."
    curl -fsSL https://bootstrap.pypa.io/get-pip.py | python3
fi
info "pip ready"

# ── 3. Download app files ────────────────────────────────────────────────────
step "Downloading Prompt Optimizer..."
mkdir -p "$INSTALL_DIR"

FILES="app.py optimizer.py analyzer.py extractor.py llm_backend.py utils.py requirements.txt menubar_app.py"
for f in $FILES; do
    curl -fsSL "$RAW/$f" -o "$INSTALL_DIR/$f"
done
info "Files downloaded to $INSTALL_DIR"

# ── 4. Install Python dependencies ───────────────────────────────────────────
step "Installing dependencies (this may take a minute)..."
python3 -m pip install -q -r "$INSTALL_DIR/requirements.txt" --upgrade
info "Dependencies installed"

# ── 5. spaCy language model ──────────────────────────────────────────────────
step "Checking spaCy language model..."
if ! python3 -c "import spacy; spacy.load('en_core_web_sm')" &>/dev/null; then
    python3 -m spacy download en_core_web_sm -q
fi
info "spaCy model ready"

# ── 6. Build the .app bundle ─────────────────────────────────────────────────
step "Building PromptOptimizer.app..."

rm -rf "$APP_DEST"
mkdir -p "$APP_DEST/Contents/MacOS"

PY_PATH=$(which python3)

cat > "$APP_DEST/Contents/MacOS/PromptOptimizer" <<LAUNCHER
#!/bin/bash
exec "$PY_PATH" "$INSTALL_DIR/menubar_app.py"
LAUNCHER

chmod +x "$APP_DEST/Contents/MacOS/PromptOptimizer"

cat > "$APP_DEST/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>PromptOptimizer</string>
    <key>CFBundleDisplayName</key><string>Prompt Optimizer</string>
    <key>CFBundleIdentifier</key><string>com.promptoptimizer.app</string>
    <key>CFBundleExecutable</key><string>PromptOptimizer</string>
    <key>CFBundleVersion</key><string>1.0</string>
    <key>CFBundleShortVersionString</key><string>1.0</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>LSUIElement</key><true/>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

# Clear quarantine so macOS doesn't block it
xattr -cr "$APP_DEST" 2>/dev/null || true
info "PromptOptimizer.app placed on Desktop"

# ── 7. Done ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}────────────────────────────────${RESET}"
echo -e "${BOLD}${GREEN}  Installation complete! ✔${RESET}"
echo -e "${BOLD}${GREEN}────────────────────────────────${RESET}"
echo ""
echo -e "  ${BOLD}Launch:${RESET}  Double-click PromptOptimizer.app on your Desktop"
echo -e "  ${BOLD}Upgrade:${RESET} Re-run this script anytime to get the latest version"
echo ""
echo -e "  ${BOLD}Want AI-quality results? (optional, free)${RESET}"
echo -e "  1. Download Ollama: ${BOLD}https://ollama.com/download${RESET}"
echo -e "  2. Run: ${BOLD}ollama pull llama3.2${RESET}"
echo -e "  3. Relaunch the app — AI mode activates automatically"
echo ""

# Auto-launch
open "$APP_DEST"
