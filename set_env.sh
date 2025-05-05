#!/usr/bin/env bash
set -euo pipefail

# 1. Remove existing virtual environments
echo "🧹 Cleaning up old virtual environments…"
[ -d ".venv" ]    && rm -rf .venv
[ -d ".venv310" ] && rm -rf .venv310

# 2. Pick a Python 3.10+ command
if   command -v python3.10 >/dev/null 2>&1; then PY=python3.10
elif command -v python    >/dev/null 2>&1; then PY=python
elif command -v py        >/dev/null 2>&1; then PY="py -3"
else
  echo "❌ Could not find Python 3.10+ (tried python3.10, python, py -3)."
  exit 1
fi
echo "🐍 Using Python interpreter: $PY"

# 3. Create the venv
echo "⚙️  Creating new venv in .venv/…"
$PY -m venv .venv

# 4. Activate the venv (Linux/macOS vs Windows Git Bash)
echo "🚀 Activating the venv…"
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
else
  echo "❌ Activation script not found in .venv!"
  exit 1
fi

# 5. Upgrade packaging tools
echo "⬆️  Upgrading pip, setuptools, wheel…"
pip install --upgrade pip setuptools wheel

# 6. Pin & install NumPy
NUMPY_VERSION="1.24.4"
echo "📌 Pinning numpy==${NUMPY_VERSION}…"
pip install --no-cache-dir --force-reinstall "numpy==${NUMPY_VERSION}"

# 7. Install your other requirements
echo "📦 Installing project requirements…"
pip install --no-cache-dir --force-reinstall -r requirements.txt

# 8. Rebuild key C-extensions from source
echo "🔨 Rebuilding sentence-transformers & llama_cpp from source…"
pip install --no-binary=:all: sentence-transformers llama_cpp

# 9. Clean up caches
echo "🗑️  Cleaning pip cache and __pycache__…"
pip cache purge || true
find . -type d -name "__pycache__" -exec rm -rf {} +

echo
echo "✅ Environment setup complete!
To activate in the future, run:
  source .venv/bin/activate   # Linux/macOS
  source .venv/Scripts/activate  # Windows (Git Bash)

Then verify & start your bot:
  python verify_gpu.py
  python test_llama_load.py
  python main.py
"
