# export_to_json.py — Export Telegram channel messages to messages.json
# Requires: pip install telethon
# Configure credentials in config.py before running.

import json
from telethon.sync import TelegramClient
import config

OUTPUT_FILE = 'messages.json'

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

all_messages = {}

try:
    with TelegramClient(config.session_name, config.api_id, config.api_hash) as client:
        # Populate Telethon's entity cache so numeric channel IDs resolve correctly
        client.get_dialogs()

        for channel in channels:
            print(f"\nFetching messages from: {channel}")
            channel_key = str(channel)
            all_messages[channel_key] = []
            try:
                for message in client.iter_messages(channel):
                    sender = message.sender
                    is_bot = bool(getattr(sender, 'bot', False))

                    if skip_bots and is_bot:
                        continue
                    if only_bots and not is_bot:
                        continue

                    sender_name = getattr(sender, 'username', None) or getattr(sender, 'first_name', None) or str(message.sender_id)
                    all_messages[channel_key].append({
                        'channel': channel_key,
                        'id': message.id,
                        'date': str(message.date),
                        'sender_id': message.sender_id,
                        'sender_name': sender_name,
                        'is_bot': is_bot,
                        'text': message.text,
                        'views': message.views,
                        'forwards': message.forwards,
                        'media': str(message.media) if message.media else None
                    })
                    if len(all_messages[channel_key]) % 100 == 0:
                        print(f"  {len(all_messages[channel_key])} messages fetched from {channel} so far...")
                print(f"  Done: {len(all_messages[channel_key])} messages from {channel}")
            except Exception as e:
                print(f"  Error fetching from {channel}: {e}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_messages, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in all_messages.values())
    print(f"\nDone! {total} messages total saved to {OUTPUT_FILE}")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channels are correct in config.py")

