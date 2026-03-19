# config.py — Telegram API credentials and channel configuration
# Edit this file with your credentials before running any export script.
# Get your api_id and api_hash from https://my.telegram.org/auth

api_id = 0                    # Replace with your integer API ID (from my.telegram.org)
api_hash = 'YOUR_API_HASH'   # Replace with your API hash string
session_name = 'anon'         # Name for the Telethon session file (anon.session)

# --- Multi-channel support ---
# List one or more channel usernames or numeric IDs to export from.
# Examples:
#   channels = ['mychannel']
#   channels = ['channel1', 'channel2', -1001234567890]
channels = [
    'channel_username',       # Replace with your channel username or numeric ID
]

# --- Backward compatibility ---
# If you still have a single `channel = ...` setting, the scripts will use it.
# channel = 'channel_username'

# --- Bot filtering ---
skip_bots = False   # When True, messages from bots are excluded from the export
only_bots = False   # When True, ONLY messages from bots are exported
