import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ["18979569"])
API_HASH = os.environ["45db354387b8122bdf6c1b0beef93743"]
BOT_TOKEN = os.environ["7764616622:AAHUES7ITI0BDrznFi5LfOf6Bpu-_Ti-p6c"]
GROUP_ID = int(os.environ["-1001589931058"])

class AutoDeleteBot(Client):
    def __init__(self):
        super().__init__(
            name="AutoDeleteBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
        )

bot = AutoDeleteBot()

@bot.on_message(filters.chat(GROUP_ID) & ~filters.service)
async def schedule_delete(client: Client, message: Message):
    sender = message.from_user.first_name if message.from_user else "Unknown"
    content = message.text or message.caption or "[Non-text message]"

    print(f"[Scheduled] From: {sender} | Message: {content} | Will delete in 1 hour.")

    async def delayed_delete():
        try:
            await asyncio.sleep(10)  # 1 hour delay
            await message.delete()
            print(f"[Deleted] Message from {sender} deleted after 1 hour.")
        except Exception as e:
            print(f"[Error] Could not delete message: {e}")

    asyncio.create_task(delayed_delete())

if __name__ == "__main__":
    print("🚀 Bot is running... Messages will be deleted 1 hour after they are posted.")
    bot.run()
