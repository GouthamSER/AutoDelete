import asyncio
from os import environ
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from aiohttp import web

# Environment variables
API_ID = int(environ.get("API_ID", "0"))
API_HASH = environ.get("API_HASH")
BOT_TOKEN = environ.get("BOT_TOKEN")
PORT_CODE = int(environ.get("PORT_CODE", "8080"))

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("API_ID, API_HASH, and BOT_TOKEN must be set as environment variables")

# Default settings
DEFAULT_DELETE_DELAY = 5
delete_delay_per_chat = {}

# Pyrogram client
app = Client(
    "auto_delete_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Helper function to get delete delay
def get_delete_delay(chat_id):
    return delete_delay_per_chat.get(chat_id, DEFAULT_DELETE_DELAY)

# Start command handler
@app.on_message(filters.command("start") & (filters.private | filters.group))
async def start_handler(client, message):
    chat_id = message.chat.id
    delay = get_delete_delay(chat_id)
    text = (
        "🤖 **Auto-Delete Bot**\n\n"
        "This bot automatically deletes all messages in groups or channels shortly after they are sent, "
        "including messages from members, admins, and the bot itself.\n\n"
        f"Messages will be deleted after {delay} seconds.\n\n"
        "Make sure to add me as an admin with 'Delete Messages' permission to work properly.\n\n"
        "Admins can change the delay with:\n"
        "`/setdelay <time>`\n\n"
        "**Examples:**\n"
        "`/setdelay 5s` - 5 seconds\n"
        "`/setdelay 2m` - 2 minutes\n"
        "`/setdelay 30` - 30 seconds (default unit)\n"
        "`/setdelay 0` - disable auto-delete"
    )
    await message.reply(text, parse_mode="markdown")

# Set delay command handler
@app.on_message(filters.command("setdelay") & filters.group)
async def set_delay_handler(client, message):
    chat_id = message.chat.id
    from_user = message.from_user

    member = await client.get_chat_member(chat_id, from_user.id)
    if member.status not in ("administrator", "creator"):
        await message.reply("❌ Only group admins can change the delete delay.")
        return

    args = message.text.split()
    if len(args) != 2:
        await message.reply(
            "Usage: /setdelay <time>\n"
            "Examples:\n"
            "/setdelay 5s (5 seconds)\n"
            "/setdelay 2m (2 minutes)\n"
            "/setdelay 30 (30 seconds)"
        )
        return

    raw = args[1].lower()

    try:
        if raw.endswith("s"):
            delay = int(raw[:-1])
        elif raw.endswith("m"):
            delay = int(raw[:-1]) * 60
        else:
            delay = int(raw)

        if delay < 0 or delay > 3600:
            await message.reply("Please provide a delay between 0 and 3600 seconds.")
            return
    except ValueError:
        await message.reply(
            "Invalid format. Use numbers with optional 's' for seconds or 'm' for minutes.\n"
            "Examples:\n"
            "/setdelay 5s\n"
            "/setdelay 2m\n"
            "/setdelay 30"
        )
        return

    delete_delay_per_chat[chat_id] = delay
    await message.reply(f"✅ Message auto-delete delay set to {delay} seconds.")

# Auto-delete logic with terminal logging
@app.on_message(filters.group | filters.channel)
async def auto_delete(client, message):
    chat_id = message.chat.id
    delay = get_delete_delay(chat_id)

    if delay == 0:
        return

    msg_content = message.text or message.caption or "[non-text message]"
    msg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{msg_time}] 📥 Message in chat {chat_id} (ID: {message.message_id}): {msg_content}")
    print(f"--> ⏳ Scheduled to delete in {delay} seconds")

    await asyncio.sleep(delay)

    try:
        await message.delete()
        deleted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{deleted_time}] ✅ Deleted message {message.message_id} from chat {chat_id}")
    except FloodWait as e:
        print(f"⚠️ FloodWait: sleeping for {e.x} seconds...")
        await asyncio.sleep(e.x)
        try:
            await message.delete()
            deleted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{deleted_time}] ✅ Deleted message {message.message_id} after waiting")
        except Exception as err:
            print(f"❌ Failed to delete message {message.message_id} after FloodWait: {err}")
    except Exception as e:
        print(f"❌ Failed to delete message {message.message_id}: {e}")

# Health check web handler
async def handle(request):
    return web.Response(text="Auto-Delete Bot is running!")

# Main function
async def main():
    await app.start()

    runner = web.AppRunner(web.Application())
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT_CODE)
    await site.start()

    print(f"🚀 Bot and webserver running on port {PORT_CODE}")

    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("🛑 Stopping bot...")

    await app.stop()
    await runner.cleanup()

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
