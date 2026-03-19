# Telegram-chats

Export messages from Telegram channels to your terminal, CSV, or JSON — optimized for **Termux** (Android terminal emulator).

---

## 📱 Termux Setup

> These steps assume you are running **Termux** on Android. Install Termux from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended over Google Play).

```bash
# 1. Update and upgrade packages
pkg update && pkg upgrade

# 2. Install Python and git
pkg install python git

# 3. Clone this repository
git clone https://github.com/kishore446/Telegram-chats.git
cd Telegram-chats

# 4. Install Python dependencies
pip install -r requirements.txt

# OR run the all-in-one setup script:
bash setup_termux.sh
```

---

## 🔑 Get Telegram API Credentials

All scripts require a Telegram API `api_id` and `api_hash`:

1. Go to <https://my.telegram.org/auth> and log in with your phone number.
2. Click **API Development Tools**.
3. Create a new application (any name/platform works).
4. Copy your **App api_id** and **App api_hash**.

---

## ⚙️ Configuration

### Using a `.env` file (recommended)

Credentials are loaded from a `.env` file so they are never accidentally committed to git.

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit .env with your real credentials (nano, vim, or any text editor)
nano .env
```

`.env` contents to fill in:

```
API_ID=12345678
API_HASH=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CHANNELS=mychannel,-1001234567890
SESSION_NAME=anon
SKIP_BOTS=False
ONLY_BOTS=False
OUTPUT_DIR=
MAX_FILE_SIZE_KB=500
```

> ⚠️ **Never share or commit your `.env` file.** It is already listed in `.gitignore` and will not be included in git commits.

### Finding channel IDs

Run `list_channels.py` to see all channels/groups you are a member of:

```bash
python list_channels.py
```

Copy the ID or username shown into the `CHANNELS` line in `.env`.

---

## 📜 Scripts

| Script | Description |
|---|---|
| `setup_termux.sh` | One-command Termux environment setup |
| `config.py` | Loads credentials & channel configuration from `.env` |
| `list_channels.py` | List all channels/groups you are a member of |
| `export_messages.py` | Print channel messages to the terminal |
| `export_to_csv.py` | Export messages to `messages.csv` |
| `export_to_json.py` | Export messages to `messages.json` (includes views, forwards, media) |

### List your channels/groups
```bash
python list_channels.py
# Prints: name, ID, member count, type (Channel / Group)
```

### Print messages to the terminal
```bash
python export_messages.py
# Shows [BOT] tag on messages sent by bots
```

### Export to CSV
```bash
python export_to_csv.py
# Creates messages.csv with all messages (columns: channel, id, date, sender_id, sender_name, is_bot, text)
# Also creates a separate file per channel: channel_<id>.csv
```

### Export to JSON
```bash
python export_to_json.py
# Creates messages.json grouped by channel:
# { "channel1": [{...}, ...], "channel2": [{...}, ...] }
# Also creates a separate file per channel: channel_<id>.json
# Each message includes: channel, id, date, sender_id, sender_name, is_bot, text, views, forwards, media
```

---

## 📂 Output Directory

By default, exported files are saved to the **current working directory**. You can change this by setting `OUTPUT_DIR` in your `.env` file.

**Termux users** — save directly to your Downloads folder:

```env
OUTPUT_DIR=/sdcard/Download
```

Then run your export as usual:

```bash
python export_to_csv.py
# Creates /sdcard/Download/messages.csv        ← combined (all channels)
# Creates /sdcard/Download/channel_-1003730302765.csv  ← per channel
# Creates /sdcard/Download/channel_-1003626740685.csv  ← per channel
# ...
```

### Per-channel files

Each export script creates **two sets of files**:

| File | Content |
|---|---|
| `messages.csv` / `messages.json` | Combined — all channels in one file |
| `channel_<id>.csv` / `channel_<id>.json` | Per-channel — one file per channel |

The per-channel files make it easy to open just the messages from a specific channel. All files are saved to `OUTPUT_DIR` if configured.

> ⚠️ If the specified directory does not exist, a warning is printed and files are saved to the current directory instead.

---

## 📏 Auto-Split Large Files

By default, any export file larger than **500 KB** is automatically split into smaller numbered parts so they can be opened on mobile apps like Google Sheets.

| Original file | → Split into |
|---|---|
| `messages.csv` (> 500 KB) | `messages_part1.csv`, `messages_part2.csv`, … |
| `channel_<id>.csv` (> 500 KB) | `channel_<id>_part1.csv`, `channel_<id>_part2.csv`, … |
| `messages.json` (> 500 KB) | `messages_part1.json`, `messages_part2.json`, … |
| `channel_<id>.json` (> 500 KB) | `channel_<id>_part1.json`, `channel_<id>_part2.json`, … |

Each part file is independently usable — CSV parts include the header row, and JSON parts are valid JSON arrays.

The original combined file is kept alongside the parts. Configure the limit in `.env`:

```env
# Maximum file size in KB before splitting (default: 500)
MAX_FILE_SIZE_KB=500
```

Terminal output shows which files were split:

```
messages.csv exceeded 500 KB, split into 2 parts: messages_part1.csv, messages_part2.csv
```

---

## 🤖 Bot Filtering

Control whether bot messages are included in the export by setting flags in `.env`:

| Setting | Effect |
|---|---|
| `SKIP_BOTS=False` (default) | All messages are exported |
| `SKIP_BOTS=True` | Messages from bots are excluded |
| `ONLY_BOTS=True` | Only messages from bots are exported |

---

## 📝 Notes

- **First run:** Telethon will ask you to enter your Telegram phone number and a verification code. This creates a `.session` file so you only authenticate once.
- **Private channels:** You must be a member or admin to export messages from a private channel.
- **Rate limits:** Telegram enforces rate limits. Exporting large channels may take time — the scripts print progress every 100 messages.
- **Multiple channels:** If one channel fails (e.g. you are not a member), the scripts continue with the remaining channels.
- **Session files:** `.session` files contain authentication tokens. They are listed in `.gitignore` and will **not** be committed to this repository.
- **Secrets safety:** Your `.env` file is listed in `.gitignore`. Running `git pull` will never overwrite your credentials.

---

## 📦 Dependencies

- [Telethon](https://docs.telethon.dev/) — pure Python Telegram MTProto client
- [python-dotenv](https://pypi.org/project/python-dotenv/) — loads `.env` files into environment variables

Install with:
```bash
pip install -r requirements.txt
```

---

## 🔗 Useful Links

- [Telethon Documentation](https://docs.telethon.dev/en/stable/)
- [Telegram API](https://core.telegram.org/api)
- [Get API Credentials](https://my.telegram.org/auth)
- [Termux (F-Droid)](https://f-droid.org/packages/com.termux/)