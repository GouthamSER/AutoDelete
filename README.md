# Telegram Auto-Delete Bot 🤖🕒

A Telegram group bot built with [Pyrogram](https://docs.pyrogram.org/) that automatically deletes messages after a set amount of time. Admins can configure the time using simple commands.

---

## 🚀 Features

- 🔥 Auto-deletes **all messages** in a group after a configurable delay.
- 👮 Only **admins** can configure settings.
- ⏰ Supports delete time in `s` (seconds), `m` (minutes), or `hr` (hours).
- 🔎 Check if a user is an admin with `/checkadmin`.

---

## 📦 Commands

| Command         | Description                                         | Who Can Use   |
|-----------------|-----------------------------------------------------|----------------|
| `/settime 10s`  | Set auto-delete time to 10 seconds                  | Admins only    |
| `/deltime`      | Show the currently set auto-delete time             | Admins only    |
| `/checkadmin`   | Check if a user is an admin (reply to a message)    | Admins only    |

---

## 🛠 Setup

### 1. Install Dependencies

```bash
pip install pyrogram tgcrypto
