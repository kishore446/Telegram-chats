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

Edit `config.py` with your credentials **before** running any script:

```python
api_id   = 12345678          # integer from my.telegram.org
api_hash = 'YOUR_API_HASH'  # string from my.telegram.org

# Export from one or more channels (username or numeric ID):
channels = [
    'mychannel',
    'another_channel',
    -1001234567890,
]

# Bot filtering (optional):
skip_bots = False   # Set True to exclude bot messages
only_bots = False   # Set True to export ONLY bot messages
```

> **Backward compatibility:** If you previously used `channel = 'username'` (single value), the scripts will still work without any changes.

### Finding channel IDs

Run `list_channels.py` to see all channels/groups you are a member of:

```bash
python list_channels.py
```

Copy the ID or username shown into the `channels` list in `config.py`.

---

## 📜 Scripts

| Script | Description |
|---|---|
| `setup_termux.sh` | One-command Termux environment setup |
| `config.py` | Central credentials & channel configuration |
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
# Creates messages.csv with columns: channel, id, date, sender_id, sender_name, is_bot, text
```

### Export to JSON
```bash
python export_to_json.py
# Creates messages.json grouped by channel:
# { "channel1": [{...}, ...], "channel2": [{...}, ...] }
# Each message includes: channel, id, date, sender_id, sender_name, is_bot, text, views, forwards, media
```

---

## 🤖 Bot Filtering

Control whether bot messages are included in the export by setting flags in `config.py`:

| Setting | Effect |
|---|---|
| `skip_bots = False` (default) | All messages are exported |
| `skip_bots = True` | Messages from bots are excluded |
| `only_bots = True` | Only messages from bots are exported |

---

## 📝 Notes

- **First run:** Telethon will ask you to enter your Telegram phone number and a verification code. This creates a `.session` file so you only authenticate once.
- **Private channels:** You must be a member or admin to export messages from a private channel.
- **Rate limits:** Telegram enforces rate limits. Exporting large channels may take time — the scripts print progress every 100 messages.
- **Multiple channels:** If one channel fails (e.g. you are not a member), the scripts continue with the remaining channels.
- **Session files:** `.session` files contain authentication tokens. They are listed in `.gitignore` and will **not** be committed to this repository.

---

## 📦 Dependencies

- [Telethon](https://docs.telethon.dev/) — pure Python Telegram MTProto client

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