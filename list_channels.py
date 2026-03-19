# list_channels.py — List all Telegram channels/groups the user is a member of
# Requires: pip install telethon
# Configure credentials in config.py before running.
# Use the IDs or usernames printed here in your config.py `channels` list.

from telethon.sync import TelegramClient
from telethon.tl.types import Channel, Chat
import config

print("Connecting to Telegram...")

try:
    with TelegramClient(config.session_name, config.api_id, config.api_hash) as client:
        print("\n{:<40} {:<20} {:<12} {}".format("Name", "ID", "Members", "Type"))
        print("-" * 80)
        for dialog in client.iter_dialogs():
            entity = dialog.entity
            if isinstance(entity, (Channel, Chat)):
                name = dialog.name or "(no name)"
                entity_id = entity.id
                # Channels use a negative ID with -100 prefix in the API
                if isinstance(entity, Channel):
                    full_id = int(f"-100{entity_id}")
                    members = getattr(entity, 'participants_count', 'N/A')
                    kind = "Channel" if not entity.megagroup else "Group (super)"
                else:
                    full_id = -entity_id
                    members = getattr(entity, 'participants_count', 'N/A')
                    kind = "Group"
                print("{:<40} {:<20} {:<12} {}".format(
                    name[:39], str(full_id), str(members), kind
                ))
        print("\nCopy an ID or username into the `channels` list in config.py.")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure your api_id and api_hash are correct in config.py")
