import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")
bot_token = os.environ.get("BOT_TOKEN", "")

if not api_id or not api_hash or not bot_token:
    raise RuntimeError("Please set API_ID, API_HASH, and BOT_TOKEN environment variables!")

delays = {}

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    await message.reply_text(
        "Hello! I'm a message deletion bot.\n"
        "Use /setdelay <seconds> in groups to set message auto-delete delay."
    )

@app.on_message(filters.command("setdelay") & filters.group)
async def setdelay_cmd(client: Client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ("administrator", "creator"):
        await message.reply_text("Only group admins can set the delay.")
        return

    if len(message.command) < 2:
        await message.reply_text("Usage: /setdelay <seconds>")
        return

    try:
        delay = int(message.command[1])
        if delay < 1:
            raise ValueError
    except ValueError:
        await message.reply_text("Please provide a valid positive integer for seconds.")
        return

    delays[message.chat.id] = delay
    await message.reply_text(f"Message auto-delete delay set to {delay} seconds.")
    print(f"[INFO] Delay set to {delay}s for chat {message.chat.title} ({message.chat.id})")

@app.on_message(filters.group & (filters.text | filters.photo | filters.video | filters.document))
async def delete_after_delay(client: Client, message: Message):
    delay = delays.get(message.chat.id)
    if not delay:
        return

    try:
        sender = await client.get_chat_member(message.chat.id, message.from_user.id)
    except Exception:
        return

    if message.from_user.is_bot:
        return

    if sender.status in ("member", "administrator", "creator"):
        print(f"[INFO] Message {message.message_id} from {message.from_user.first_name} "
              f"in chat '{message.chat.title}' will be deleted in {delay} seconds.")
        await asyncio.sleep(delay)
        try:
            await message.delete()
            print(f"[INFO] Deleted message {message.message_id} from {message.from_user.first_name} "
                  f"in chat '{message.chat.title}' after {delay} seconds.")
        except Exception as e:
            print(f"[ERROR] Failed to delete message {message.message_id}: {e}")

if __name__ == "__main__":
    app.run()
