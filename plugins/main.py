from pyrogram import filters, Client
from pyrogram.types import Message
import asyncio

@Client.on_message(filters.group)
async def handle_group_message(client, message):
    chat_title = message.chat.title or "Unknown Chat"
    chat_id = message.chat.id
    sender_name = message.from_user.first_name if message.from_user else "Unknown Sender"

    if message.text:
        content = message.text
    else:
        content = "Non-text message"

    print(f"[{chat_title} | {chat_id}] {sender_name}: {content}")

    # Schedule deletion after 1 hour
    await asyncio.sleep(5)
    try:
        await message.delete()
        print(f"Deleted message {message.message_id} from {sender_name}")
    except Exception as e:
        print(f"Failed to delete message {message.message_id}: {e}")


