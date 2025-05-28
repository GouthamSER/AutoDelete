from pyrogram import filters, Client
from pyrogram.types import Message

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    welcome_text = (
        "👋 Hello!\n\n"
        "I automatically delete messages sent in groups **30 min** after they are posted to avoid copyright issues.\n"
        "I also print all group messages to the terminal for monitoring.\n\n"
        "__Add me to your groups and make sure I have permission to delete messages!__"
    )
    await message.reply_text(welcome_text, disable_web_page_preview=True)
