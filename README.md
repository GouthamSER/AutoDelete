# 🧹 Telegram Auto-Delete Bot (Pyrogram)

This is a simple Telegram bot built using **Pyrogram**. It automatically deletes messages in group chats after a specified delay (like `10s`, `2m`, `1hr`) and persists the settings using **SQLite** so the timers remain active even after bot restarts.

---

## ⚙️ Features

- Set auto-delete timer per group using `/settime`
- Check current timer using `/deltime`
- Auto-delete any message after the configured delay
- Admin-only access control
- Persistent settings using SQLite

---

## 🚀 Commands

| Command       | Description                                 | Access       |
|---------------|---------------------------------------------|--------------|
| `/settime 10s`| Set message delete timer (e.g., 10s, 2m)    | Admins only  |
| `/deltime`    | Show current delete timer                   | Admins only  |

---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/telegram-auto-delete-bot.git
cd telegram-auto-delete-bot
