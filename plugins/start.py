from pyrogram import filters
from pyrogram.types import Message

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply_text(
        "Hello! I'm a message deletion bot.\n"
        "Use /setdelay <seconds> in groups to set message auto-delete delay."
    )
