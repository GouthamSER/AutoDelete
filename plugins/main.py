from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
from info import ADMINS  # Your global admins list
from db import set_delete_time as db_set_time, get_delete_time as db_get_time, load_all_delete_times

# In-memory storage (loaded from DB at startup)
delete_times = load_all_delete_times()

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
    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        return await message.reply("❌ Only group admins or bot admins can use this command.")

    if len(message.command) < 2:
        return await message.reply("Usage: /settime 10s | 2m | 1hr")

    seconds = parse_time(message.command[1])
    if seconds is None:
        return await message.reply("Invalid format. Use: 10s, 2m, 1hr")

    delete_times[chat_id] = seconds
    db_set_time(chat_id, seconds)  # Save to DB
    await message.reply(f"✅ Auto-delete time set to {message.command[1]}")

@Client.on_message(filters.command("deltime") & filters.group)
async def get_delete_time(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        return await message.reply("❌ Only group admins or bot admins can use this command.")

    seconds = db_get_time(chat_id)
    if not seconds:
        return await message.reply("No auto-delete time set for this group.")

    if seconds < 60:
        time_str = f"{seconds}s"
    elif seconds < 3600:
        time_str = f"{seconds // 60}m"
    else:
        time_str = f"{seconds // 3600}hr"

    await message.reply(f"🕒 Auto-delete time is set to {time_str}")

@Client.on_message(filters.group & ~filters.command(["settime", "deltime"]))
async def handle_group_message(client: Client, message: Message):
    chat_id = message.chat.id
    delay = delete_times.get(chat_id)

    if not delay:
        return

    # Message preview
    if message.text:
        preview = message.text
    elif message.photo:
        preview = "📷 Photo"
    elif message.sticker:
        preview = f"🧩 Sticker: {message.sticker.emoji}"
    elif message.video:
        preview = "🎥 Video"
    elif message.document:
        preview = f"📄 {message.document.file_name}"
    elif message.audio:
        preview = f"🎵 {message.audio.title or 'Audio File'}"
    else:
        preview = "🔸 Non-text message"

    sender = message.from_user.first_name if message.from_user else "Unknown"
    chat_title = message.chat.title or "Unknown Group"

    print(f"[{chat_title} | {chat_id}] {sender} sent: {preview}")

    # Wait and delete
    await asyncio.sleep(delay)
    try:
        await message.delete()
        print(f"✅ Deleted message from {sender} in '{chat_title}'")
    except Exception as e:
        print(f"❌ Failed to delete message: {e}")
