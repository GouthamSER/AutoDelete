from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
from info import ADMINS  

# 🧠 In-memory storage for delete times per group
delete_times = {}  # { chat_id: delay_in_seconds }

# ⏱️ Parse time string like "10s", "5m", "1hr"
def parse_time(time_str):
    match = re.match(r"(\d+)(s|m|h|hr)$", time_str.lower())
    if not match:
        return None
    val, unit = match.groups()
    val = int(val)
    if unit == "s":
        return val
    elif unit == "m":
        return val * 60
    elif unit in ("h", "hr"):
        return val * 3600
    return None

# 🛠️ Command: /settime (only allowed Telegram user IDs)
@Client.on_message(filters.command("settime") & filters.group)
async def set_delete_time(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    if user_id not in ADMINS:
        return await message.reply("❌ You are not authorized to use this command.")

    chat_id = message.chat.id

    if len(message.command) < 2:
        return await message.reply("Usage: /settime 10s | 2m | 1hr")

    seconds = parse_time(message.command[1])
    if seconds is None:
        return await message.reply("Invalid format. Use: 10s, 2m, 1hr")

    delete_times[chat_id] = seconds
    await message.reply(f"✅ Auto-delete time set to {message.command[1]}")

# ℹ️ Command: /deltime (only allowed user IDs)
@Client.on_message(filters.command("deltime") & filters.group)
async def get_delete_time(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    if user_id not in ADMINS:
        return await message.reply("❌ You are not authorized to use this command.")

    chat_id = message.chat.id
    seconds = delete_times.get(chat_id)

    if not seconds:
        return await message.reply("No auto-delete time set for this group.")

    if seconds < 60:
        time_str = f"{seconds}s"
    elif seconds < 3600:
        time_str = f"{seconds // 60}m"
    else:
        time_str = f"{seconds // 3600}hr"

    await message.reply(f"🕒 Auto-delete time is set to {time_str}")

# 🧹 Delete text messages after the configured delay
@Client.on_message(filters.text & filters.group)
async def handle_group_message(client: Client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "Unknown Group"
    sender = message.from_user.first_name if message.from_user else "Unknown User"
    content = message.text or "Non-text message"

    # 🔍 Log to terminal
    print(f"[{chat_title} | {chat_id}] {sender}: {content}")

    delay = delete_times.get(chat_id)
    if not delay:
        return  # No deletion set

    await asyncio.sleep(delay)
    try:
        await message.delete()
        print(f"✅ Deleted message {message.id} from {sender} in '{chat_title}' ({chat_id})")
    except Exception as e:
        print(f"❌ Failed to delete message {message.id} from {sender}: {e}")

