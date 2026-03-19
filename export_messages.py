# export_messages.py — Print Telegram channel messages to the terminal
# Requires: pip install telethon
# Configure credentials in config.py before running.

from telethon.sync import TelegramClient
import config

print("Connecting to Telegram...")

try:
    with TelegramClient(config.session_name, config.api_id, config.api_hash) as client:
        print(f"Fetching messages from: {config.channel}\n")
        for message in client.iter_messages(config.channel):
            print(f"[{message.id}] {message.date} | sender: {message.sender_id}")
            print(f"  {message.text}\n")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id, api_hash, and channel are correct in config.py")
