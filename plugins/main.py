from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
from info import ADMINS  # <-- Global bot admin(s)

# In-memory delete time store
delete_times = {}

def parse_time(time_str):
    match = re.match(r"^(\d+)(s|m|h|hr)$", time_str.lower().strip())
    if not match:
        return None
    val, unit = match.groups()
    val = int(val)
    return val * {"s": 1, "m": 60, "h": 3600, "hr": 3600}[unit]

async def is_authorized(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False

@Client.on_message(filters.command("settime") & filters.group)
async def set_delete_time(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        return await message.reply("❌ Only group admins or bot admins can use this command.")

    if len(message.command) < 2:
        return await message.reply("Usage: /settime 10s | 2m | 1hr")

    seconds = parse_time(message.command[1])
    if seconds is None:
        return await message.reply("Invalid format. Use: 10s, 2m, 1hr")

    delete_times[chat_id] = seconds
    print(f"✅ Auto-delete time set to {seconds}s for chat {chat_id}")
    await message.reply(f"✅ Auto-delete time set to {message.command[1]}")

@Client.on_message(filters.command("deltime") & filters.group)
async def get_delete_time(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        return await message.reply("❌ Only group admins or bot admins can use this command.")

    seconds = delete_times.get(chat_id)
    if not seconds:
        return await message.reply("No auto-delete time set for this group.")

    if seconds < 60:
        time_str = f"{seconds}s"
    elif seconds < 3600:
        time_str = f"{seconds // 60}m"
    else:
        time_str = f"{seconds // 3600}hr"

    print(f"🕒 Group {chat_id} has delete time: {time_str}")
    await message.reply(f"🕒 Auto-delete time is set to {time_str}")

@Client.on_message(filters.group & ~filters.command(["settime", "deltime"]))
async def auto_delete_user_messages(client: Client, message: Message):
    chat_id = message.chat.id
    delay = delete_times.get(chat_id)

    if not delay:
        return

    preview = message.text[:50] if message.text else "Non-text message"
    sender = message.from_user.first_name if message.from_user else "Unknown"

    print(f"[{chat_id}] User '{sender}' sent: {preview}")

    await asyncio.sleep(delay)
    try:
        await message.delete()
        print(f"✅ Deleted user message from '{sender}' in chat {chat_id}")
    except Exception as e:
        print(f"❌ Failed to delete user message: {e}")

@Client.on_message(filters.group & filters.me & filters.text)
async def auto_delete_bot_messages(client: Client, message: Message):
    chat_id = message.chat.id
    delay = delete_times.get(chat_id)

    if not delay:
        return

    preview = message.text[:50]
    print(f"[{chat_id}] Bot sent: {preview}")

    await asyncio.sleep(delay)
    try:
        await message.delete()
        print(f"✅ Deleted bot message in chat {chat_id}")
    except Exception as e:
        print(f"❌ Failed to delete bot message: {e}")
