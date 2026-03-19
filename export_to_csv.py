# export_to_csv.py — Export Telegram channel messages to messages.csv
# Requires: pip install telethon
# Configure credentials in config.py before running.

import csv
from telethon.sync import TelegramClient
import config

OUTPUT_FILE = 'messages.csv'

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

total_count = 0

try:
    with TelegramClient(config.session_name, config.api_id, config.api_hash) as client, \
         open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:

        writer = csv.writer(f)
        writer.writerow(['channel', 'id', 'date', 'sender_id', 'sender_name', 'is_bot', 'text'])

        for channel in channels:
            print(f"\nFetching messages from: {channel}")
            count = 0
            try:
                for message in client.iter_messages(channel):
                    sender = message.sender
                    is_bot = bool(getattr(sender, 'bot', False))

                    if skip_bots and is_bot:
                        continue
                    if only_bots and not is_bot:
                        continue

                    sender_name = getattr(sender, 'username', None) or getattr(sender, 'first_name', None) or str(message.sender_id)
                    writer.writerow([channel, message.id, message.date, message.sender_id, sender_name, is_bot, message.text])
                    count += 1
                    if count % 100 == 0:
                        print(f"  {count} messages exported from {channel} so far...")
                print(f"  Done: {count} messages from {channel}")
                total_count += count
            except Exception as e:
                print(f"  Error fetching from {channel}: {e}")

    print(f"\nDone! {total_count} messages total saved to {OUTPUT_FILE}")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channels are correct in config.py")

