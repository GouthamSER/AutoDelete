# 🤖 AutoDelete Telegram Bot

A Telegram bot built using [Pyrogram](https://docs.pyrogram.org/) that automatically deletes messages from any group (public or private) after a configurable delay. It also logs deleted messages and supports admin-only commands for managing settings.

---

## 🚀 Features

- ✅ Auto-deletes **all messages** (including bot's own) after a set time in environ.
- 🛡️ Supports **public and private groups**.
- 📄 Logs deleted messages to a local file (`log.txt`).
- ℹ️ `/start` command for both groups and private chats.

---

## 🧠 How It Works

- Messages in any group (except service messages like "user joined") are scheduled for deletion.
- Each group can set its own custom delete time.
- Messages are deleted after the specified delay.
- Deleted messages are logged with group ID, sender, and content.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/GouthamSER/AutoDelete
cd AutoDelete
