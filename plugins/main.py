from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
import asyncio
import re

# In-memory storage of group deletion times
delete_times = {}  # chat_id -> time in seconds

# Helper to parse time like 1s, 2m, 1hr
def parse_time(time_str: str) -> int:
    match = re.match(r"(\d+)(s|m|h|hr)$", time_str.lower())
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit in ("h", "hr"):
        return value * 3600
    return None

# Only admins can set the deletion time
@Client.on_message(filters.command("setdeltime", prefixes="/") & filters.group)
async def set_delete_time(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Check if user is admin
    member = await client.get_chat_member(chat_id, user_id)
    if not (member.status in ("administrator", "creator")):
        await message.reply("Only admins can set delete time.")
        return

    # Extract time argument
    try:
        time_arg = message.command[1]  # /setdeltime 2m
    except IndexError:
        await message.reply("Usage: /setdeltime 10s | 5m | 1hr")
        return

    seconds = parse_time(time_arg)
    if seconds is None:
        await message.reply("Invalid time format. Use: 10s | 5m | 1hr")
        return

    delete_times[chat_id] = seconds
    await message.reply(f"Auto-delete time set to {time_arg}")

# Handle all group messages for deletion
@Client.on_message(filters.text & filters.group)
async def handle_group_message(client: Client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "Unknown Chat"
    sender_name = message.from_user.first_name if message.from_user else "Unknown Sender"
    content = message.text

    print(f"{datetime.now()} - [{chat_title} | {chat_id}] {sender_name}: {content}")

    delay = delete_times.get(chat_id)
    if delay:
        await asyncio.sleep(delay)
        try:
            await message.delete()
            print(f"Deleted message {message.id} from {sender_name}")
        except Exception as e:
            print(f"Failed to delete message {message.id}: {e}")

@Client.on_message(filters.command("deltime", prefixes="/") & filters.group)
async def get_delete_time(client: Client, message: Message):
    chat_id = message.chat.id

    delay = delete_times.get(chat_id)
    if not delay:
        await message.reply("No auto-delete time is set for this group.")
        return

    # Convert seconds back to human-readable
    if delay < 60:
        time_str = f"{delay}s"
    elif delay < 3600:
        time_str = f"{delay // 60}m"
    else:
        time_str = f"{delay // 3600}hr"

    await message.reply(f"Current auto-delete time is set to: **{time_str}**")
