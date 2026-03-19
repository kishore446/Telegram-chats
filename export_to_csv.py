# export_to_csv.py — Export Telegram channel messages to CSV files
# Requires: pip install telethon
# Configure credentials in config.py before running.

import csv
import os
import re
from telethon.sync import TelegramClient
import config

output_base = getattr(config, 'output_dir', '')
OUTPUT_FILE = os.path.join(output_base, 'messages.csv') if output_base else 'messages.csv'

FIELDNAMES = ['channel', 'id', 'date', 'sender_id', 'sender_name', 'is_bot', 'text']

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

# Collect rows per channel so we can write both combined and per-channel files
channel_rows = {}
total_count = 0

try:
    with TelegramClient(config.session_name, config.api_id, config.api_hash) as client:
        # Populate Telethon's entity cache so numeric channel IDs resolve correctly
        client.get_dialogs()

        for channel in channels:
            print(f"\nFetching messages from: {channel}")
            channel_key = str(channel)
            channel_rows[channel_key] = []
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
                    channel_rows[channel_key].append([channel, message.id, message.date, message.sender_id, sender_name, is_bot, message.text])
                    count += 1
                    if count % 100 == 0:
                        print(f"  {count} messages exported from {channel} so far...")
                print(f"  Done: {count} messages from {channel}")
                total_count += count
            except Exception as e:
                print(f"  Error fetching from {channel}: {e}")

    # Write combined file
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(FIELDNAMES)
        for rows in channel_rows.values():
            writer.writerows(rows)

    saved_files = [OUTPUT_FILE]

    # Write per-channel files
    for channel_key, rows in channel_rows.items():
        safe_name = re.sub(r'[^\w\-]', '_', channel_key)
        per_channel_file = os.path.join(output_base, f'channel_{safe_name}.csv') if output_base else f'channel_{safe_name}.csv'
        with open(per_channel_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(FIELDNAMES)
            writer.writerows(rows)
        saved_files.append(per_channel_file)

    print(f"\nDone! {total_count} messages total")
    print("Files saved:")
    for saved in saved_files:
        print(f"  {saved}")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channels are correct in config.py")

