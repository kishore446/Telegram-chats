# export_to_csv.py — Export Telegram channel messages to CSV files
# Requires: pip install telethon
# Configure credentials in config.py before running.

import csv
import math
import os
import re
from telethon.sync import TelegramClient
import config

max_file_size_bytes = getattr(config, 'max_file_size_kb', 500) * 1024


def _split_csv_file(filepath, fieldnames):
    """Split a CSV file into multiple parts if it exceeds max_file_size_bytes.

    Returns a list of part file paths if splitting occurred, or an empty list
    if the file is within the size limit.
    """
    file_size = os.path.getsize(filepath)
    if file_size <= max_file_size_bytes:
        return []

    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    if not rows:
        return []

    avg_row_size = file_size / (len(rows) + 1)  # +1 for header
    # Use a 0.95 safety factor so parts stay comfortably under the limit
    rows_per_part = max(1, math.floor(max_file_size_bytes * 0.95 / avg_row_size))

    base, ext = os.path.splitext(filepath)
    part_files = []
    part_num = 1
    for start in range(0, len(rows), rows_per_part):
        chunk = rows[start:start + rows_per_part]
        part_path = f'{base}_part{part_num}{ext}'
        with open(part_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(chunk)
        part_files.append(part_path)
        part_num += 1

    return part_files

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

    # Split combined file if it exceeds the size limit
    parts = _split_csv_file(OUTPUT_FILE, FIELDNAMES)
    if parts:
        part_names = ', '.join(parts)
        print(f"{OUTPUT_FILE} exceeded {config.max_file_size_kb} KB, split into {len(parts)} parts: {part_names}")
        saved_files.extend(parts)

    # Write per-channel files
    for channel_key, rows in channel_rows.items():
        safe_name = re.sub(r'[^\w\-]', '_', channel_key)
        per_channel_file = os.path.join(output_base, f'channel_{safe_name}.csv') if output_base else f'channel_{safe_name}.csv'
        with open(per_channel_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(FIELDNAMES)
            writer.writerows(rows)
        saved_files.append(per_channel_file)

        # Split per-channel file if it exceeds the size limit
        parts = _split_csv_file(per_channel_file, FIELDNAMES)
        if parts:
            part_names = ', '.join(parts)
            print(f"{per_channel_file} exceeded {config.max_file_size_kb} KB, split into {len(parts)} parts: {part_names}")
            saved_files.extend(parts)

    print(f"\nDone! {total_count} messages total")
    print("Files saved:")
    for saved in saved_files:
        print(f"  {saved}")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channels are correct in config.py")

