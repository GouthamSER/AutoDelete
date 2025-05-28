import os
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from aiohttp import web

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT_CODE = int(os.getenv("PORT_CODE", "8080"))  # Set your port or default 8080

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("API_ID, API_HASH, and BOT_TOKEN must be set as environment variables")

DEFAULT_DELETE_DELAY = 5
delete_delay_per_chat = {}

app = Client(
    "auto_delete_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def get_delete_delay(chat_id):
    return delete_delay_per_chat.get(chat_id, DEFAULT_DELETE_DELAY)

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

@app.on_message(filters.group | filters.channel)
async def auto_delete(client, message):
    chat_id = message.chat.id
    delay = get_delete_delay(chat_id)

    if delay == 0:
        return

    await asyncio.sleep(delay)

    try:
        await message.delete()
    except FloodWait as e:
        print(f"Sleeping for {e.x} seconds due to FloodWait...")
        await asyncio.sleep(e.x)
        try:
            await message.delete()
        except Exception as err:
            print(f"Failed to delete message {message.message_id} after floodwait: {err}")
    except Exception as e:
        print(f"Failed to delete message {message.message_id}: {e}")

# Simple aiohttp handler example
async def handle(request):
    return web.Response(text="Auto-Delete Bot is running!")

async def main():
    await app.start()  # Start Pyrogram client

    # Setup aiohttp webserver
    runner = web.AppRunner(web.Application())
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT_CODE)
    await site.start()

    print(f"Bot and webserver running on port {PORT_CODE}")

    # Keep running until cancelled
    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("Stopping...")

    await app.stop()
    await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
