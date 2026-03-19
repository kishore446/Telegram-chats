# export_messages.py — Print Telegram channel messages to the terminal
# Requires: pip install telethon
# Configure credentials in config.py before running.

from telethon.sync import TelegramClient
import config

# Resolve channel list (supports both `channels` list and legacy `channel` single value)
channels = getattr(config, 'channels', None)
if not channels:
    legacy = getattr(config, 'channel', None)
    channels = [legacy] if legacy else []

skip_bots = getattr(config, 'skip_bots', False)
only_bots = getattr(config, 'only_bots', False)

if skip_bots and only_bots:
    print("Warning: skip_bots and only_bots are both True — no messages will be exported.")

print("Connecting to Telegram...")

try:
    with TelegramClient(config.session_name, config.api_id, config.api_hash) as client:
        # Populate Telethon's entity cache so numeric channel IDs resolve correctly
        client.get_dialogs()

        for channel in channels:
            print(f"\n{'='*60}")
            print(f"Fetching messages from: {channel}")
            print('='*60)
            try:
                for message in client.iter_messages(channel):
                    sender = message.sender
                    is_bot = bool(getattr(sender, 'bot', False))

                    if skip_bots and is_bot:
                        continue
                    if only_bots and not is_bot:
                        continue

                    bot_tag = ' [BOT]' if is_bot else ''
                    sender_name = getattr(sender, 'username', None) or getattr(sender, 'first_name', None) or str(message.sender_id)
                    print(f"[{message.id}] {message.date} | {channel} | sender: {sender_name}{bot_tag}")
                    print(f"  {message.text}\n")
            except Exception as e:
                print(f"  Error fetching from {channel}: {e}")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channels are correct in config.py")

