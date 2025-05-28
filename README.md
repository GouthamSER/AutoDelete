# 🧹 Telegram Auto-Delete Bot

A powerful yet simple Telegram bot built with [Pyrogram](https://docs.pyrogram.org/) to **automatically delete group messages** after a configurable delay. Ideal for maintaining clean and time-sensitive discussion groups.

---

## 🚀 Features

- ⏱️ Configurable auto-delete timer per group
- 🔒 Command access restricted to specific Telegram user IDs
- 📋 Supports duration in `seconds`, `minutes`, or `hours` (e.g. `30s`, `5m`, `1hr`)
- 📥 Logs message content and deletion status to the terminal
- 💬 Handles only text messages (non-text types can be added easily)

---

## ⚙️ Environment Variables

Set the following environment variables in your `.env` file or hosting platform (e.g., Heroku):

| Variable     | Description                                      |
|--------------|--------------------------------------------------|
| `API_ID`     | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH`   | Telegram API Hash                                |
| `BOT_TOKEN`  | Bot token from [@BotFather](https://t.me/BotFather) |
| `ADMINS`     | Space-separated list of Telegram user IDs allowed to use commands |
| `DEL_TIME`   | (Optional) Default auto-delete time in seconds   |

**Example `.env` file:**

```env
API_ID=123456
API_HASH=abcdef1234567890abcdef1234567890
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMINS=8435734848 1122334455
DEL_TIME=600
