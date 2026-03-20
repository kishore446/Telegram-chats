# interactive_export.py — Interactive channel selector and exporter for Termux
# Requires: pip install telethon
# Configure credentials in config.py before running.
#
# Usage:
#   python interactive_export.py
#
# On-screen menu lets you pick which channels to export and in what format.

import csv
import json
import math
import os
import re
import shutil
import sys

from telethon.sync import TelegramClient
from telethon.tl.types import Channel, Chat

import config

# ---------------------------------------------------------------------------
# Constants / settings (read from config, same as other export scripts)
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_BYTES = getattr(config, 'max_file_size_kb', 500) * 1024
MAX_FILE_SIZE_KB = MAX_FILE_SIZE_BYTES // 1024
OUTPUT_BASE = getattr(config, 'output_dir', '')
SKIP_BOTS = getattr(config, 'skip_bots', False)
ONLY_BOTS = getattr(config, 'only_bots', False)

CSV_FIELDNAMES = ['channel', 'id', 'date', 'sender_id', 'sender_name', 'is_bot', 'text']

SEP = '\u2500' * 50  # ──────────────────────────────────────────────────────


# ---------------------------------------------------------------------------
# File-splitting helpers (mirrored from export_to_csv / export_to_json)
# ---------------------------------------------------------------------------

def _split_csv_file(filepath, fieldnames):
    """Split a CSV file into parts if it exceeds MAX_FILE_SIZE_BYTES.
    Returns list of part paths created, or empty list if no split needed."""
    file_size = os.path.getsize(filepath)
    if file_size <= MAX_FILE_SIZE_BYTES:
        return []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    if not rows:
        return []
    avg_row_size = file_size / (len(rows) + 1)
    rows_per_part = max(1, math.floor(MAX_FILE_SIZE_BYTES * 0.95 / avg_row_size))
    base, ext = os.path.splitext(filepath)
    part_files = []
    for part_num, start in enumerate(range(0, len(rows), rows_per_part), start=1):
        chunk = rows[start:start + rows_per_part]
        part_path = f'{base}_part{part_num}{ext}'
        with open(part_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(chunk)
        part_files.append(part_path)
    return part_files


def _split_json_file(filepath, messages):
    """Split a JSON file into parts if it exceeds MAX_FILE_SIZE_BYTES.
    Returns list of part paths created, or empty list if no split needed."""
    file_size = os.path.getsize(filepath)
    if file_size <= MAX_FILE_SIZE_BYTES:
        return []
    if not messages:
        return []
    avg_msg_size = file_size / len(messages)
    msgs_per_part = max(1, math.floor(MAX_FILE_SIZE_BYTES * 0.95 / avg_msg_size))
    base, ext = os.path.splitext(filepath)
    part_files = []
    for part_num, start in enumerate(range(0, len(messages), msgs_per_part), start=1):
        chunk = messages[start:start + msgs_per_part]
        part_path = f'{base}_part{part_num}{ext}'
        with open(part_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
        part_files.append(part_path)
    return part_files


def _out(filename):
    """Return the full output path for a file, respecting OUTPUT_BASE."""
    return os.path.join(OUTPUT_BASE, filename) if OUTPUT_BASE else filename


# ---------------------------------------------------------------------------
# Channel-listing helper
# ---------------------------------------------------------------------------

def fetch_channels(client):
    """Return a list of (name, full_id, kind) tuples for all Channel/Chat dialogs."""
    channels = []
    for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, (Channel, Chat)):
            name = dialog.name or "(no name)"
            if isinstance(entity, Channel):
                full_id = int(f"-100{entity.id}")
                kind = "Channel" if not entity.megagroup else "Group (super)"
            else:
                full_id = -entity.id
                kind = "Group"
            channels.append((name, full_id, kind))
    return channels


# ---------------------------------------------------------------------------
# Selection parsing
# ---------------------------------------------------------------------------

def parse_selection(raw, total):
    """Parse a selection string into a list of 0-based indices.

    Accepts:
      - 'all' or 'a'  → all channels
      - single number  → '3'
      - comma list     → '1,3,4'
      - range          → '2-4'
      - combinations   → '1,3-5,7'

    Returns a sorted list of valid 0-based indices, or None on error.
    """
    raw = raw.strip().lower()
    if raw in ('all', 'a'):
        return list(range(total))

    indices = set()
    for part in raw.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            # Could be a range like '1-3'
            bounds = part.split('-')
            if len(bounds) == 2 and bounds[0].strip().isdigit() and bounds[1].strip().isdigit():
                lo = int(bounds[0].strip())
                hi = int(bounds[1].strip())
                if lo < 1 or hi < lo or hi > total:
                    return None
                indices.update(range(lo - 1, hi))
            else:
                return None
        elif part.isdigit():
            n = int(part)
            if n < 1 or n > total:
                return None
            indices.add(n - 1)
        else:
            return None

    return sorted(indices) if indices else None


# ---------------------------------------------------------------------------
# Export logic
# ---------------------------------------------------------------------------

def export_channel(client, channel_id, fmt):
    """Fetch messages from one channel and return (csv_rows, json_messages, count).

    fmt: 'csv', 'json', 'both', or 'terminal'
    Rows / messages are only populated for the formats that are needed.
    count is always the total number of messages processed (respecting bot filters).
    """
    csv_rows = []
    json_msgs = []
    count = 0

    for message in client.iter_messages(channel_id):
        sender = message.sender
        is_bot = bool(getattr(sender, 'bot', False))

        if SKIP_BOTS and is_bot:
            continue
        if ONLY_BOTS and not is_bot:
            continue

        sender_name = (
            getattr(sender, 'username', None)
            or getattr(sender, 'first_name', None)
            or str(message.sender_id)
        )

        if fmt in ('csv', 'both'):
            csv_rows.append([
                str(channel_id),
                message.id,
                message.date,
                message.sender_id,
                sender_name,
                is_bot,
                message.text,
            ])

        if fmt in ('json', 'both'):
            json_msgs.append({
                'channel': str(channel_id),
                'id': message.id,
                'date': str(message.date),
                'sender_id': message.sender_id,
                'sender_name': sender_name,
                'is_bot': is_bot,
                'text': message.text,
                'views': message.views,
                'forwards': message.forwards,
                'media': str(message.media) if message.media else None,
            })

        if fmt == 'terminal':
            bot_tag = ' [BOT]' if is_bot else ''
            print(f"  [{message.date}] {sender_name}{bot_tag}: {message.text or ''}")

        count += 1
        if count % 100 == 0:
            print(f"  {count} messages fetched so far...")

    return csv_rows, json_msgs, count


def write_csv(all_csv_rows, selected_channels):
    """Write combined + per-channel CSV files. Returns list of saved file paths."""
    saved = []

    combined_path = _out('messages.csv')
    with open(combined_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_FIELDNAMES)
        for rows in all_csv_rows.values():
            writer.writerows(rows)
    saved.append(combined_path)
    parts = _split_csv_file(combined_path, CSV_FIELDNAMES)
    if parts:
        print(f"  {combined_path} exceeded {MAX_FILE_SIZE_KB} KB, split into {len(parts)} parts.")
        saved.extend(parts)

    for channel_id, rows in all_csv_rows.items():
        safe = re.sub(r'[^\w\-]', '_', str(channel_id))
        path = _out(f'channel_{safe}.csv')
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_FIELDNAMES)
            writer.writerows(rows)
        saved.append(path)
        parts = _split_csv_file(path, CSV_FIELDNAMES)
        if parts:
            print(f"  {path} exceeded {MAX_FILE_SIZE_KB} KB, split into {len(parts)} parts.")
            saved.extend(parts)

    return saved


def write_json(all_json_msgs, selected_channels):
    """Write combined + per-channel JSON files. Returns list of saved file paths."""
    saved = []

    combined_path = _out('messages.json')
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(all_json_msgs, f, ensure_ascii=False, indent=2)
    saved.append(combined_path)
    all_msgs_flat = [msg for msgs in all_json_msgs.values() for msg in msgs]
    if os.path.getsize(combined_path) > MAX_FILE_SIZE_BYTES:
        parts = _split_json_file(combined_path, all_msgs_flat)
        if parts:
            print(f"  {combined_path} exceeded {MAX_FILE_SIZE_KB} KB, split into {len(parts)} parts.")
            saved.extend(parts)

    for channel_id, msgs in all_json_msgs.items():
        safe = re.sub(r'[^\w\-]', '_', str(channel_id))
        path = _out(f'channel_{safe}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(msgs, f, ensure_ascii=False, indent=2)
        saved.append(path)
        parts = _split_json_file(path, msgs)
        if parts:
            print(f"  {path} exceeded {MAX_FILE_SIZE_KB} KB, split into {len(parts)} parts.")
            saved.extend(parts)

    return saved


# ---------------------------------------------------------------------------
# Interactive prompts
# ---------------------------------------------------------------------------

def prompt_channels(channels):
    """Display channel list and return user-selected (name, full_id, kind) tuples."""
    print()
    print("Your channels and groups:")
    print(SEP)
    print(f"  {'#':<4} {'Name':<30} {'ID':<22} Type")
    print(SEP)
    for i, (name, full_id, kind) in enumerate(channels, start=1):
        print(f"  {i:<4} {name[:29]:<30} {str(full_id):<22} {kind}")
    print(SEP)
    print()
    print("Enter channel numbers to export (comma-separated), or 'all' for everything:")
    print("  Examples:  2      1,3      1-3      all")
    print("  Type 'q' or 'quit' to exit.")
    print()

    while True:
        try:
            raw = input("> ").strip()
        except EOFError:
            raw = 'q'

        if raw.lower() in ('q', 'quit'):
            print("\nBye!")
            sys.exit(0)

        indices = parse_selection(raw, len(channels))
        if indices is None:
            print(f"  ⚠️  Invalid selection. Enter numbers between 1 and {len(channels)}, or 'all'.")
            continue

        selected = [channels[i] for i in indices]
        return selected


def prompt_format():
    """Prompt user for export format. Returns 'csv', 'json', 'both', or 'terminal'."""
    print()
    print("Export format:")
    print("  1. CSV  (messages.csv)")
    print("  2. JSON (messages.json)")
    print("  3. Both")
    print("  4. Terminal only (print to screen)")
    print()

    fmt_map = {'1': 'csv', '2': 'json', '3': 'both', '4': 'terminal'}
    while True:
        try:
            raw = input("Choose [1-4]: ").strip()
        except EOFError:
            raw = '1'
        if raw in fmt_map:
            return fmt_map[raw]
        print("  ⚠️  Please enter 1, 2, 3, or 4.")


def prompt_copy_to_downloads(saved_files):
    """Ask if the user wants to copy files to /sdcard/Download."""
    downloads = '/sdcard/Download'
    if not os.path.isdir(downloads):
        return  # Not on Android / no Downloads folder — skip silently

    print()
    try:
        answer = input(f"Copy files to {downloads}? [Y/n]: ").strip().lower()
    except EOFError:
        answer = 'n'

    if answer in ('', 'y', 'yes'):
        copied = 0
        for path in saved_files:
            if os.path.isfile(path):
                try:
                    shutil.copy2(path, downloads)
                    copied += 1
                except Exception as e:
                    print(f"  ⚠️  Could not copy {path}: {e}")
        if copied:
            print(f"✅ {copied} file(s) copied to {downloads}/")
        else:
            print("  No files were copied.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if SKIP_BOTS and ONLY_BOTS:
        print("Warning: SKIP_BOTS and ONLY_BOTS are both True — no messages will be exported.")

    print("Connecting to Telegram...")

    try:
        with TelegramClient(config.session_name, config.api_id, config.api_hash) as client:
            # Populate entity cache and fetch channel list
            channels = fetch_channels(client)

            if not channels:
                print("No channels or groups found. Make sure you are a member of at least one channel.")
                return

            # Step 1 — channel selection
            selected = prompt_channels(channels)
            if not selected:
                print("No channels selected. Exiting.")
                return

            # Step 2 — format selection
            fmt = prompt_format()

            # Step 3 — export
            print()
            all_csv_rows = {}
            all_json_msgs = {}
            total_messages = 0

            for name, full_id, kind in selected:
                print(f"\nFetching messages from: {name} ({full_id})")
                try:
                    csv_rows, json_msgs, count = export_channel(client, full_id, fmt)
                except Exception as e:
                    print(f"  ⚠️  Error fetching from {name}: {e}")
                    continue

                print(f"  Done: {count} messages from {name}")
                total_messages += count

                if fmt in ('csv', 'both'):
                    all_csv_rows[str(full_id)] = csv_rows
                if fmt in ('json', 'both'):
                    all_json_msgs[str(full_id)] = json_msgs

            # Step 4 — write files
            saved_files = []

            if fmt in ('csv', 'both') and all_csv_rows:
                saved_files.extend(write_csv(all_csv_rows, selected))

            if fmt in ('json', 'both') and all_json_msgs:
                saved_files.extend(write_json(all_json_msgs, selected))

            # Step 5 — summary
            print()
            print(f"✅ Done! Exported {total_messages} messages from {len(selected)} channel(s).")

            if saved_files:
                print()
                print("Files saved:")
                for path in saved_files:
                    try:
                        size_kb = os.path.getsize(path) / 1024
                        print(f"  📄 {path} ({size_kb:.0f} KB)")
                    except OSError:
                        print(f"  📄 {path}")

                # Step 6 — offer to copy to Downloads
                prompt_copy_to_downloads(saved_files)

    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure your api_id and api_hash are correct in config.py")
        sys.exit(1)


if __name__ == '__main__':
    main()
