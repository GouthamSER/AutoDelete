from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
from info import ADMINS  # List of bot admin user IDs

delete_times = {}
DEFAULT_DELETE_TIME = 300  # Default delete time (5 minutes) if none is set

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
    except Exception as e:
        print(f"Authorization check failed: {e}")
        return False

async def get_user_status(client: Client, chat_id: int, user_id: int) -> str:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status == "creator":
            return "creator (owner)"
        elif member.status == "administrator":
            return "administrator"
        else:
            return "not an admin or creator"
    except Exception as e:
        print(f"Failed to check user status: {e}")
        return "unknown (possibly not in the group/channel or bot lacks permissions)"

async def delete_user_message(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
        print(f"✅ Deleted message from {msg.from_user.first_name if msg.from_user else 'Unknown'} in {msg.chat.id}")
    except Exception as e:
        print(f"❌ Failed to delete user message: {e}")

async def delete_bot_message(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
        print(f"✅ Deleted bot message in chat {msg.chat.id}")
    except Exception as e:
        print(f"❌ Failed to delete bot message: {e}")

@Client.on_message(filters.command("settime") & filters.group)
async def set_delete_time(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        print(f"Unauthorized /settime attempt by {message.from_user.first_name} (ID: {user_id}) in chat {chat_id}")
        return await message.reply("❌ Only group/channel admins or bot admins can use this command.")

    if len(message.command) < 2:
        return await message.reply("Usage: /settime 10s | 2m | 1hr")

    seconds = parse_time(message.command[1])
    if seconds is None:
        return await message.reply("Invalid format. Use: 10s, 2m, 1hr")

    delete_times[chat_id] = seconds
    print(f"🛠️ Auto-delete time set to {seconds}s for chat {chat_id}")
    msg = await message.reply(f"✅ Auto-delete time set to {message.command[1]}")
    await delete_bot_message(msg, seconds)

@Client.on_message(filters.command("deltime") & filters.group)
async def get_delete_time(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        print(f"Unauthorized /deltime attempt by {message.from_user.first_name} (ID: {user_id}) in chat {chat_id}")
        return await message.reply("❌ Only group/channel admins or bot admins can use this command.")

    seconds = delete_times.get(chat_id, DEFAULT_DELETE_TIME)
    if seconds < 60:
        time_str = f"{seconds}s"
    elif seconds < 3600:
        time_str = f"{seconds // 60}m"
    else:
        time_str = f"{seconds // 3600}hr"

    print(f"ℹ️ Group {chat_id} has delete time: {time_str}")
    msg = await message.reply(f"🕒 Auto-delete time is set to {time_str}")
    await delete_bot_message(msg, seconds)

@Client.on_message(filters.command("checkadmin") & filters.group)
async def check_admin_status(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        print(f"Unauthorized /checkadmin attempt by {message.from_user.first_name} (ID: {user_id}) in chat {chat_id}")
        return await message.reply("❌ Only group/channel admins or bot admins can use this command.")

    # Determine target user
    target_user_id = None
    target_user_name = "Unknown"
    
    if message.reply_to_message and message.reply_to_message.from_user:
        target_user_id = message.reply_to_message.from_user.id
        target_user_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1 and message.command[1].isdigit():
        target_user_id = int(message.command[1])
    else:
        return await message.reply("Please reply to a user’s message or provide a user ID (e.g., /checkadmin 123456789).")

    # Check target user's status
    status = await get_user_status(client, chat_id, target_user_id)
    msg = await message.reply(f"User {target_user_name} (ID: {target_user_id}) is {status} in this group/channel.")
    await delete_bot_message(msg, delete_times.get(chat_id, DEFAULT_DELETE_TIME))

@Client.on_message(filters.group)
async def auto_delete_everything(client: Client, message: Message):
    chat_id = message.chat.id
    delay = delete_times.get(chat_id, DEFAULT_DELETE_TIME)

    sender_name = (
        message.from_user.first_name if message.from_user else
        ("System" if message.service else "Unknown")
    )
    content = message.text or message.caption or "📎 Non-text message"
    print(f"[{chat_id}] {sender_name} sent: {content[:50]}")

    await delete_user_message(message, delay)
