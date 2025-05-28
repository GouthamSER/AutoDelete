import os
from pyrogram import filters, Client
from pyrogram.types import Message
import asyncio

# Get deletion delay from environment variable (default to 1800 seconds)
DEL_TIME = int(os.getenv("DEL_TIME", 1800))

@Client.on_message(filters.group)
async def handle_group_message(client, message):
    chat_title = message.chat.title or "Unknown Chat"
    chat_id = message.chat.id
    sender_name = message.from_user.first_name if message.from_user else "Unknown Sender"
    content = message.text if message.text else "Non-text message"

    print(f"[{chat_title} | {chat_id}] {sender_name}: {content}")

    asyncio.create_task(delete_message_later(message))

async def delete_message_later(message: Message):
    await asyncio.sleep(DEL_TIME)
    try:
        await message.delete()
        print(f"Deleted message {message.id} from {message.from_user.first_name}")
    except Exception as e:
        print(f"Failed to delete message {message.id}: {e}")
