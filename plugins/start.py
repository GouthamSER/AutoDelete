from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.private & filters.command("start"))
async def start_command(client: Client, message: Message):
    welcome_text = (
        "👋 Hello!\n\n"
        "I'm a group message cleaner bot.\n"
        "➤ When added to a group, I monitor all messages.\n"
        "➤ Messages will automatically be **deleted after a set delay**.\n\n"
        "🕒 Current deletion delay: {} seconds.\n"
        "⚙️ You can configure this via an environment variable or a config file.\n\n"
        "Add me to your group and give me permission to delete messages!"
    ).format(DEL_TIME)

    await message.reply(welcome_text)