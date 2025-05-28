import asyncio
from os import environ
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from aiohttp import web


class AutoDeleteBot:
    def __init__(self):
        self.api_id = int(environ.get("API_ID", "0"))
        self.api_hash = environ.get("API_HASH")
        self.bot_token = environ.get("BOT_TOKEN")
        self.port = int(environ.get("PORT_CODE", "8080"))

        if not self.api_id or not self.api_hash or not self.bot_token:
            raise Exception("API_ID, API_HASH, and BOT_TOKEN must be set as environment variables")

        self.default_delay = 5
        self.delete_delay_per_chat = {}

        self.app = Client("auto_delete_bot", api_id=self.api_id, api_hash=self.api_hash, bot_token=self.bot_token)

        self.app.add_handler(filters.command("start") & (filters.private | filters.group), self.start_handler)
        self.app.add_handler(filters.command("setdelay") & filters.group, self.set_delay_handler)
        self.app.add_handler(filters.group | filters.channel, self.auto_delete)

    def get_delay(self, chat_id):
        return self.delete_delay_per_chat.get(chat_id, self.default_delay)

    async def start_handler(self, client, message):
        delay = self.get_delay(message.chat.id)
        text = (
            "🤖 **Auto-Delete Bot**\n\n"
            "This bot automatically deletes all messages shortly after they are sent.\n"
            f"Current delay: {delay} seconds\n"
            "Use `/setdelay <time>` to change delay. E.g., `/setdelay 10s`, `/setdelay 2m`, `/setdelay 30`"
        )
        await message.reply(text, parse_mode="markdown")

    async def set_delay_handler(self, client, message):
        chat_id = message.chat.id
        user = message.from_user

        member = await client.get_chat_member(chat_id, user.id)
        if member.status not in ("administrator", "creator"):
            await message.reply("❌ Only admins can change delay.")
            return

        parts = message.text.split()
        if len(parts) != 2:
            await message.reply("Usage: `/setdelay 10s`, `/setdelay 2m`, `/setdelay 30`", parse_mode="markdown")
            return

        raw = parts[1].lower()
        try:
            if raw.endswith("s"):
                delay = int(raw[:-1])
            elif raw.endswith("m"):
                delay = int(raw[:-1]) * 60
            else:
                delay = int(raw)
            if not (0 <= delay <= 3600):
                raise ValueError
        except ValueError:
            await message.reply("❌ Invalid format. Use seconds (`s`), minutes (`m`), or plain number.")
            return

        self.delete_delay_per_chat[chat_id] = delay
        await message.reply(f"✅ Delay set to {delay} seconds.")

    async def auto_delete(self, client, message):
        chat_id = message.chat.id
        delay = self.get_delay(chat_id)

        if delay == 0:
            return

        msg_text = message.text or message.caption or "[non-text]"
        print(f"📩 Message {message.message_id} in {chat_id}: {msg_text} (delete in {delay}s)")

        await asyncio.sleep(delay)

        try:
            await message.delete()
            print(f"✅ Deleted message {message.message_id} from chat {chat_id}")
        except FloodWait as e:
            print(f"⚠️ FloodWait: sleeping for {e.x}s")
            await asyncio.sleep(e.x)
            await message.delete()
        except Exception as e:
            print(f"❌ Error deleting message {message.message_id}: {e}")

    async def web_handler(self, request):
        return web.Response(text="Auto-Delete Bot is running!")

    async def run(self):
        await self.app.start()
        print("🤖 Bot started.")

        runner = web.AppRunner(web.Application())
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()
        print(f"🌐 Web server running on port {self.port}")

        try:
            while True:
                await asyncio.sleep(3600)
        except (asyncio.CancelledError, KeyboardInterrupt):
            print("🛑 Shutting down...")

        await self.app.stop()
        await runner.cleanup()


if __name__ == "__main__":
    bot = AutoDeleteBot()
    asyncio.run(bot.run())
