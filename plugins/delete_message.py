import asyncio
from pyrogram import filters
from pyrogram.types import Message

@Client.on_message(filters.group & (filters.text | filters.photo | filters.video | filters.document))
async def delete_after_delay(client, message: Message):
    if not hasattr(client, "delays"):
        return

    delay = client.delays.get(message.chat.id)
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
