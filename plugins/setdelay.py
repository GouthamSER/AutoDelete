from pyrogram import filters
from pyrogram.types import Message

# We'll store delays in bot's "storage" to share between plugins
# You can attach a dictionary attribute to client for simplicity
@Client.on_message(filters.command("setdelay") & filters.group)
async def setdelay_cmd(client, message: Message):
    # Initialize delay storage dict if not exist
    if not hasattr(client, "delays"):
        client.delays = {}

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

    client.delays[message.chat.id] = delay
    await message.reply_text(f"Message auto-delete delay set to {delay} seconds.")
    print(f"[INFO] Delay set to {delay}s for chat '{message.chat.title}' ({message.chat.id})")
