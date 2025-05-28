from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
from info import ADMINS

# 🧠 In-memory storage for delete times per group
delete_times = {}  # { chat_id: delay_in_seconds }

# ⏱️ Parse time string (e.g., "10s", "5m", "1hr")
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

# 🛠️ Command: /settime 10s | 2m | 1hr (only allowed user IDs)
@Client.on_message(filters.command("settime") & filters.group)
async def set_delete_time(client: Client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("❌ You are not authorized to use this command.")

    chat_id = message.chat.id

    if len(message.command) < 2:
        return await message.reply("Usage: /settime 10s | 2m | 1hr")

    seconds = parse_time(message.command[1])
    if seconds is None:
        return await message.reply("Invalid format. Use: 10s, 2m, 1hr")

    delete_times[chat_id] = seconds
    await message.reply(f"✅ Auto-delete time set to {message.command[1]}")

# ℹ️ Command: /deltime — get current delete time (only allowed user IDs)
@Client.on_message(filters.command("deltime") & filters.group)
async def get_delete_time(client: Client, message: Message):
    if message.from_user.id not in ADMINS:
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

# 🧹 Auto-delete group text messages after set delay
@Client.on_message(filters.text & filters.group)
async def handle_group_message(client: Client, message: Message):
    chat_id = message.chat.id
    delay = delete_times.get(chat_id)
    if not delay:
        return  # No deletion configured for this group

    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"❌ Failed to delete message {message.id}: {e}")
