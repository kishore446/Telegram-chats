# clean_exports.py — Delete all previously exported CSV/JSON files
#
# Usage:
#   python clean_exports.py          # interactive (asks for confirmation)
#   python clean_exports.py --yes    # skip confirmation (for scripting)
#   python clean_exports.py -y       # same as --yes

import argparse
import glob as _glob
import os
import sys

import config

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

OUTPUT_BASE = getattr(config, 'output_dir', '')

# Glob patterns that match exported files only — never .py, .env, .session, etc.
EXPORT_PATTERNS = [
    'messages.csv',
    'messages.json',
    'messages_part*.csv',
    'messages_part*.json',
    'channel_*.csv',
    'channel_*.json',
    'channel_*_part*.csv',
    'channel_*_part*.json',
]

DOWNLOADS_DIR = '/sdcard/Download'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fmt_size(size_bytes):
    """Return a human-readable file size string (e.g. '902 KB', '1.4 MB')."""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / 1024:.0f} KB"


def find_exported_files(directory):
    """Return a sorted, deduplicated list of exported file paths in *directory*."""
    found = []
    seen = set()
    for pattern in EXPORT_PATTERNS:
        for path in sorted(_glob.glob(os.path.join(directory, pattern))):
            if os.path.isfile(path) and path not in seen:
                seen.add(path)
                found.append(path)
    return found


def delete_files(files):
    """Delete each file in *files* and return the count of successfully deleted files."""
    deleted = 0
    for path in files:
        try:
            os.remove(path)
            deleted += 1
        except Exception as e:
            print(f"  \u26a0\ufe0f  Could not delete {path}: {e}")
    return deleted


def clean_directory(directory, auto_yes):
    """Scan *directory* for exported files and delete them (with optional confirmation).

    Returns True if any files were deleted, False otherwise.
    """
    files = find_exported_files(directory)

    if not files:
        print(f"No exported files found in {directory}. Nothing to clean!")
        return False

    print(f"\nFound {len(files)} exported file(s) in {directory}:")
    for path in files:
        try:
            size = os.path.getsize(path)
            print(f"  \U0001f4c4 {os.path.basename(path)} ({fmt_size(size)})")
        except OSError:
            print(f"  \U0001f4c4 {os.path.basename(path)}")

    print()

    if auto_yes:
        answer = 'y'
    else:
        try:
            answer = input(f"Delete all {len(files)} file(s)? [y/N]: ").strip().lower()
        except EOFError:
            answer = 'n'

    if answer in ('y', 'yes'):
        deleted = delete_files(files)
        print(f"\u2705 Cleared {deleted} file(s) from {directory}/")
        return True
    else:
        print("Cancelled. No files deleted.")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Delete all previously exported Telegram CSV/JSON files.",
    )
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help="Skip confirmation prompt and delete files immediately.",
    )
    args = parser.parse_args()

    # Empty OUTPUT_BASE means "current directory" (same convention as interactive_export.py)
    output_dir = OUTPUT_BASE if OUTPUT_BASE else '.'

    # Clean primary output directory
    clean_directory(output_dir, args.yes)

    # Offer to also clean /sdcard/Download (if it exists and is different from output_dir)
    if os.path.isdir(DOWNLOADS_DIR) and os.path.abspath(DOWNLOADS_DIR) != os.path.abspath(output_dir):
        dl_files = find_exported_files(DOWNLOADS_DIR)
        if dl_files:
            print()
            if args.yes:
                answer = 'y'
            else:
                try:
                    answer = input(f"Also clear exported files from {DOWNLOADS_DIR}? [y/N]: ").strip().lower()
                except EOFError:
                    answer = 'n'

            if answer in ('y', 'yes'):
                deleted = delete_files(dl_files)
                print(f"\u2705 Cleared {deleted} file(s) from {DOWNLOADS_DIR}/")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
