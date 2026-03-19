#!/data/data/com.termux/files/usr/bin/bash
# setup_termux.sh — Set up the environment for Telegram message export on Termux
# Usage: bash setup_termux.sh

echo "=========================================="
echo " Telegram Chat Exporter — Termux Setup"
echo "=========================================="
echo ""

echo "[1/3] Updating package lists..."
pkg update -y && pkg upgrade -y

echo ""
echo "[2/3] Installing Python and git..."
pkg install -y python git

echo ""
echo "[3/3] Installing required Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo " Setup complete!"
echo ""
echo " Next steps:"
echo "  1. Edit config.py with your API credentials"
echo "     (Get them from https://my.telegram.org/auth)"
echo "  2. Run one of the export scripts:"
echo "     python export_messages.py   — print to terminal"
echo "     python export_to_csv.py     — save to messages.csv"
echo "     python export_to_json.py    — save to messages.json"
echo "=========================================="
