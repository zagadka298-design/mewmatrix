#!/usr/bin/env bash
set -e

# ==============================================================================
# 🐱 MewMatrix Universal Installer & Updater
# One-line install / update command:
#   curl -sSL https://raw.githubusercontent.com/zagadka298-design/mewmatrix/main/install.sh | bash
# ==============================================================================

echo "🐱 Installing / Updating MewMatrix..."

# Verify python3 is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Error: python3 is required but not installed." >&2
    echo "Please install Python 3.8 or newer and try again." >&2
    exit 1
fi

# Verify Python version >= 3.8
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]); then
    echo "❌ Error: Python 3.8+ is required (found $PY_VER)." >&2
    exit 1
fi

# Choose destination directory
if [ "$(id -u)" -eq 0 ]; then
    INSTALL_DIR="/usr/local/bin"
else
    INSTALL_DIR="$HOME/.local/bin"
fi

mkdir -p "$INSTALL_DIR"

SCRIPT_PATH="$INSTALL_DIR/mewmatrix"
ALIAS_PATH="$INSTALL_DIR/meowmatrix"

RAW_URL="https://raw.githubusercontent.com/zagadka298-design/mewmatrix/main/mewmatrix.py"
echo "📥 Fetching latest MewMatrix from GitHub..."

# Clean up broken / old symlinks or obsolete pipx wrappers that cause version conflicts
if [ -L "$SCRIPT_PATH" ]; then
    rm -f "$SCRIPT_PATH"
fi
if [ -L "$ALIAS_PATH" ]; then
    rm -f "$ALIAS_PATH"
fi

# Download to a temporary file first
TMP_FILE="$INSTALL_DIR/mewmatrix.tmp.$$"
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$RAW_URL" -o "$TMP_FILE"
elif command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP_FILE" "$RAW_URL"
else
    echo "❌ Error: Neither curl nor wget was found. Please install one of them." >&2
    exit 1
fi

# Validate Python code syntax before installation
if ! python3 -m py_compile "$TMP_FILE" 2>/dev/null; then
    echo "❌ Error: Downloaded code failed Python syntax verification." >&2
    rm -f "$TMP_FILE"
    exit 1
fi

# Atomically move into place and make executable
mv "$TMP_FILE" "$SCRIPT_PATH"
chmod +x "$SCRIPT_PATH"

# Create symlink for meowmatrix
ln -sf "$SCRIPT_PATH" "$ALIAS_PATH"

# Clean up any stale python bytecode in INSTALL_DIR
rm -rf "$INSTALL_DIR/__pycache__"

# Ensure INSTALL_DIR is in user's PATH
PATH_ADDED=0
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    SHELL_PROFILE=""
    case "$SHELL" in
        */zsh)
            SHELL_PROFILE="$HOME/.zshrc"
            ;;
        */bash)
            if [ -f "$HOME/.bashrc" ]; then
                SHELL_PROFILE="$HOME/.bashrc"
            elif [ -f "$HOME/.bash_profile" ]; then
                SHELL_PROFILE="$HOME/.bash_profile"
            fi
            ;;
        *)
            if [ -f "$HOME/.profile" ]; then
                SHELL_PROFILE="$HOME/.profile"
            fi
            ;;
    esac

    if [ -n "$SHELL_PROFILE" ]; then
        if ! grep -q "$INSTALL_DIR" "$SHELL_PROFILE" 2>/dev/null; then
            echo "" >> "$SHELL_PROFILE"
            echo "# Added by MewMatrix installer" >> "$SHELL_PROFILE"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_PROFILE"
            PATH_ADDED=1
        fi
    fi
fi

VERSION=$("$SCRIPT_PATH" --version 2>/dev/null || echo "2.2.0")

echo ""
echo "✨ ========================================="
echo "🐱 $VERSION successfully installed!"
echo "✨ ========================================="
echo ""
echo "Usage:"
echo "  mewmatrix              # Run classic matrix rain"
echo "  mewmatrix meow         # Cat emoji rain mode 🐱"
echo "  mewmatrix rainbow      # Rainbow colors mode 🌈"
echo "  mewmatrix red cyan     # Mix any color combinations"
echo "  mewmatrix --update     # Automatically check and update"
echo ""

if [ "$PATH_ADDED" -eq 1 ]; then
    echo "ℹ️  Added $INSTALL_DIR to PATH in $SHELL_PROFILE."
    echo "   To start using immediately in this terminal session, run:"
    echo "   export PATH=\"$INSTALL_DIR:\$PATH\""
    echo ""
fi
