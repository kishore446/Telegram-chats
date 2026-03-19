# export_to_csv.py — Export Telegram channel messages to messages.csv
# Requires: pip install telethon
# Configure credentials in config.py before running.

import csv
from telethon.sync import TelegramClient
import config

OUTPUT_FILE = 'messages.csv'

print("Connecting to Telegram...")

try:
    with TelegramClient(config.session_name, config.api_id, config.api_hash) as client, \
         open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:

        writer = csv.writer(f)
        writer.writerow(['id', 'date', 'sender_id', 'text'])

        print(f"Fetching messages from: {config.channel}")
        count = 0
        for message in client.iter_messages(config.channel):
            writer.writerow([message.id, message.date, message.sender_id, message.text])
            count += 1
            if count % 100 == 0:
                print(f"  {count} messages exported so far...")

    print(f"\nDone! {count} messages saved to {OUTPUT_FILE}")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channel are correct in config.py")
