# export_to_json.py — Export Telegram channel messages to messages.json
# Requires: pip install telethon
# Configure credentials in config.py before running.

import json
from telethon.sync import TelegramClient
import config

OUTPUT_FILE = 'messages.json'

print("Connecting to Telegram...")

messages_list = []

try:
    with TelegramClient(config.session_name, config.api_id, config.api_hash) as client:
        print(f"Fetching messages from: {config.channel}")
        for message in client.iter_messages(config.channel):
            messages_list.append({
                'id': message.id,
                'date': str(message.date),
                'sender_id': message.sender_id,
                'text': message.text,
                'views': message.views,
                'forwards': message.forwards,
                'media': str(message.media) if message.media else None
            })
            if len(messages_list) % 100 == 0:
                print(f"  {len(messages_list)} messages fetched so far...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages_list, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(messages_list)} messages saved to {OUTPUT_FILE}")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channel are correct in config.py")
