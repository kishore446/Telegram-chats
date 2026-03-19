# export_to_json.py — Export Telegram channel messages to JSON files
# Requires: pip install telethon
# Configure credentials in config.py before running.

import json
import math
import os
import re
from telethon.sync import TelegramClient
import config

max_file_size_bytes = getattr(config, 'max_file_size_kb', 500) * 1024


def _split_json_file(filepath, messages):
    """Split a JSON file into multiple parts if it exceeds max_file_size_bytes.

    messages must be a list of message dicts (the content already written to filepath).
    Returns a list of part file paths if splitting occurred, or an empty list
    if the file is within the size limit.
    """
    file_size = os.path.getsize(filepath)
    if file_size <= max_file_size_bytes:
        return []

    if not messages:
        return []

    avg_msg_size = file_size / len(messages)
    # Use a 0.95 safety factor so parts stay comfortably under the limit
    msgs_per_part = max(1, math.floor(max_file_size_bytes * 0.95 / avg_msg_size))

    base, ext = os.path.splitext(filepath)
    part_files = []
    part_num = 1
    for start in range(0, len(messages), msgs_per_part):
        chunk = messages[start:start + msgs_per_part]
        part_path = f'{base}_part{part_num}{ext}'
        with open(part_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
        part_files.append(part_path)
        part_num += 1

    return part_files

output_base = getattr(config, 'output_dir', '')
OUTPUT_FILE = os.path.join(output_base, 'messages.json') if output_base else 'messages.json'

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

    saved_files = [OUTPUT_FILE]

    # Split combined file if it exceeds the size limit
    if os.path.getsize(OUTPUT_FILE) > max_file_size_bytes:
        all_msgs_list = [msg for msgs in all_messages.values() for msg in msgs]
        parts = _split_json_file(OUTPUT_FILE, all_msgs_list)
        if parts:
            part_names = ', '.join(parts)
            print(f"{OUTPUT_FILE} exceeded {config.max_file_size_kb} KB, split into {len(parts)} parts: {part_names}")
            saved_files.extend(parts)

    # Write per-channel files
    for channel_key, messages in all_messages.items():
        safe_name = re.sub(r'[^\w\-]', '_', channel_key)
        per_channel_file = os.path.join(output_base, f'channel_{safe_name}.json') if output_base else f'channel_{safe_name}.json'
        with open(per_channel_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        saved_files.append(per_channel_file)

        # Split per-channel file if it exceeds the size limit
        parts = _split_json_file(per_channel_file, messages)
        if parts:
            part_names = ', '.join(parts)
            print(f"{per_channel_file} exceeded {config.max_file_size_kb} KB, split into {len(parts)} parts: {part_names}")
            saved_files.extend(parts)

    total = sum(len(v) for v in all_messages.values())
    print(f"\nDone! {total} messages total")
    print("Files saved:")
    for saved in saved_files:
        print(f"  {saved}")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channels are correct in config.py")

