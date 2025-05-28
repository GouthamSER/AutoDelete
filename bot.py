import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired

# Load credentials from environment variables
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Delete time per group (default 3600 seconds = 1 hour)
group_delete_times = {}

# Telegram Bot
class AutoDeleteBot(Client):
    def __init__(self):
        super().__init__(
            name="AutoDeleteBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
        )

bot = AutoDeleteBot()

# Utility: Check if user is admin
async def is_user_admin(chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except ChatAdminRequired:
        return False

# Auto-delete messages
@bot.on_message(filters.group & ~filters.service)
async def schedule_delete(client: Client, message: Message):
    group_id = message.chat.id
    sender = message.from_user.first_name if message.from_user else "Bot"
    content = message.text or message.caption or "[Non-text message]"
    delete_time = group_delete_times.get(group_id, 3600)

    print(f"[Scheduled] From: {sender} | Group: {group_id} | Message: {content} | Deleting in {delete_time}s")

    async def delayed_delete():
        try:
            await asyncio.sleep(delete_time)
            await message.delete()
            with open("log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"[Group: {group_id}] {sender}: {content}\n")
            print(f"[Deleted] Message from {sender}")
        except Exception as e:
            print(f"[Error] Could not delete message: {e}")

    asyncio.create_task(delayed_delete())

# Admin command: set delete time
@bot.on_message(filters.command("setdeletetime") & filters.group)
async def set_delete_time(client: Client, message: Message):
    if not await is_user_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can set delete time.")
    try:
        minutes = int(message.command[1])
        group_delete_times[message.chat.id] = minutes * 60
        await message.reply(f"✅ Messages will now be deleted after {minutes} minutes.")
    except (IndexError, ValueError):
        await message.reply("⚠️ Usage: /setdeletetime <minutes>")

# Admin command: get delete time
@bot.on_message(filters.command("getdeletetime") & filters.group)
async def get_delete_time(client: Client, message: Message):
    if not await is_user_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can check delete time.")
    seconds = group_delete_times.get(message.chat.id, 3600)
    minutes = seconds // 60
    await message.reply(f"⏲️ Current delete time: {minutes} minutes.")

# /start command in private chat
@bot.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    await message.reply_text(
        "👋 I auto-delete messages in your group after a configurable time.\n\n"
        "Admin commands:\n"
        "• /setdeletetime <minutes>\n"
        "• /getdeletetime"
    )

# /start command in groups
@bot.on_message(filters.command("start") & filters.group)
async def start_group(client: Client, message: Message):
    reply = await message.reply("✅ I'm running! I’ll auto-delete messages after the configured time.")
    await asyncio.sleep(10)
    await reply.delete()

# Main entry point
if __name__ == "__main__":
    print("🤖 Starting Telegram Bot...")
    bot.run()
