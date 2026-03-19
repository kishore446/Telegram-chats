# config.py — Telegram API credentials and channel configuration
# Values are loaded from a .env file when available.
# Copy .env.example to .env and fill in your credentials:
#   cp .env.example .env
# Get your api_id and api_hash from https://my.telegram.org/auth

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; fall back to environment variables only

# --- API credentials ---
_raw_api_id = os.environ.get('API_ID', '')
_raw_api_hash = os.environ.get('API_HASH', '')

# Detect whether the user has set real credentials
_using_default_id = not _raw_api_id or _raw_api_id in ('0', '12345678', 'YOUR_API_ID_HERE')
_using_default_hash = not _raw_api_hash or _raw_api_hash in ('YOUR_API_HASH', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

if _using_default_id or _using_default_hash:
    print("ERROR: Telegram API credentials are not configured.")
    print("  Please copy .env.example to .env and fill in your API_ID and API_HASH:")
    print("    cp .env.example .env")
    print("  Then edit .env with your credentials from https://my.telegram.org/auth")
    sys.exit(1)

try:
    api_id = int(_raw_api_id)
except ValueError:
    print(f"ERROR: API_ID must be an integer, got: {_raw_api_id!r}")
    print("  Edit your .env file and set API_ID to the numeric ID from https://my.telegram.org/auth")
    sys.exit(1)

api_hash = _raw_api_hash

# --- Session name ---
session_name = os.environ.get('SESSION_NAME', 'anon')

# --- Channel list ---
# CHANNELS env var: comma-separated usernames or numeric IDs.
# Example: CHANNELS=channel1,-1001234567890,channel2
_raw_channels = os.environ.get('CHANNELS', '')
if _raw_channels:
    channels = []
    for entry in _raw_channels.split(','):
        entry = entry.strip()
        if not entry:
            continue
        try:
            channels.append(int(entry))
        except ValueError:
            channels.append(entry)
else:
    # Fallback placeholder so scripts still load; they will skip an empty list gracefully.
    channels = []
    print("WARNING: No channels configured. Set CHANNELS in your .env file.")
    print("  Example: CHANNELS=mychannel,-1001234567890")

# --- Output directory ---
output_dir = os.environ.get('OUTPUT_DIR', '').strip()
if output_dir and not os.path.isdir(output_dir):
    print(f"WARNING: OUTPUT_DIR '{output_dir}' does not exist. Files will be saved to the current directory.")
    output_dir = ''

# --- Bot filtering ---
def _parse_bool(value, default: bool = False) -> bool:
    if not value:
        return default
    return value.strip().lower() in ('1', 'true', 'yes')

skip_bots = _parse_bool(os.environ.get('SKIP_BOTS', ''))
only_bots = _parse_bool(os.environ.get('ONLY_BOTS', ''))
