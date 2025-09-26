from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
from info import ADMINS
from plugins.db import set_autodelete as set_delete_time, get_autodelete as get_delete_time
from pyrogram.errors import FloodWait

# =========================
# Helper Functions
# =========================

def parse_time(time_str):
    match = re.match(r"^(\d+)(s|m|h|hr)$", time_str.lower().strip())
    if not match:
        return None
    val, unit = match.groups()
    val = int(val)
    return val * {"s": 1, "m": 60, "h": 3600, "hr": 3600}[unit]

async def is_authorized(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        print(f"Authorization check failed: {e}")
        return False

async def get_user_status(client: Client, chat_id: int, user_id: int) -> str:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status == "creator":
            return "creator (owner)"
        elif member.status == "administrator":
            return "administrator"
        else:
            return "not an admin or creator"
    except Exception as e:
        print(f"Failed to check user status: {e}")
        return "unknown"

async def delete_user_message(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception as e:
        print(f"❌ Failed to delete user message: {e}")

async def delete_bot_message(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception as e:
        print(f"❌ Failed to delete bot message: {e}")


# =========================
# Admin Commands (Groups Only)
# =========================

@Client.on_message(filters.command("settime") & filters.group)
async def set_delete_time_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        return await message.reply("❌ Only admins can use this command.")

    if len(message.command) < 2:
        return await message.reply("Usage: /settime 10s | 2m | 1hr")

    seconds = parse_time(message.command[1])
    if seconds is None:
        return await message.reply("Invalid format. Use: 10s, 2m, 1hr")

    set_delete_time(chat_id, seconds)
    msg = await message.reply(f"✅ Auto-delete time set to {message.command[1]}")
    await delete_bot_message(msg, seconds)


@Client.on_message(filters.command("deltime") & filters.group)
async def get_delete_time_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        return await message.reply("❌ Only admins can use this command.")

    seconds = get_delete_time(chat_id)
    if seconds is None:
        return await message.reply("❌ No auto-delete time set for this group.")

    if seconds < 60:
        time_str = f"{seconds}s"
    elif seconds < 3600:
        time_str = f"{seconds // 60}m"
    else:
        time_str = f"{seconds // 3600}hr"

    msg = await message.reply(f"🕒 Auto-delete time is set to {time_str}")
    await delete_bot_message(msg, seconds)


@Client.on_message(filters.command("checkadmin") & filters.group)
async def check_admin_status(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_authorized(client, chat_id, user_id):
        return await message.reply("❌ Only admins can use this command.")

    target_user_id = None
    target_user_name = "Unknown"

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user_id = message.reply_to_message.from_user.id
        target_user_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1 and message.command[1].isdigit():
        target_user_id = int(message.command[1])
    else:
        return await message.reply("Reply to a user or provide a user ID.")

    status = await get_user_status(client, chat_id, target_user_id)
    msg = await message.reply(f"User {target_user_name} (ID: {target_user_id}) is {status}.")
    
    seconds = get_delete_time(chat_id)
    if seconds:
        await delete_bot_message(msg, seconds)


# =========================
# Spam Protection + Auto Delete (PM + Groups)
# =========================

# Suspicious domains (extended list with shorteners)
SUSPICIOUS_DOMAINS = [
    # Your existing ones
    "xyz", "top", "online", "shop", "click", "fun", "live", "site",
    "space", "buzz", "club", "cam", "link", "rest", "work",

    # Common spammy TLDs
    "icu", "best", "fit", "today", "monster", "gq", "ml", "cf", "tk",
    "party", "stream", "download", "racing", "men", "date", "loan", "cricket",
    "surf", "host", "press", "pw", "review", "accountant", "science", "win",
    "bid", "faith", "trade", "webcam", "sexy", "porn", "xxx",

    # Suspicious marketing/crypto/etc
    "beauty", "hair", "makeup", "skin", "diet", "cheap", "free", "shop",
    "money", "deal", "offers", "discount", "gift", "lotto", "bet", "casino",
    "crypto", "token", "nft",

    # Popular shorteners
    "bit\.ly", "cutt\.ly", "tinyurl\.com", "t\.co", "shorturl\.at", "is\.gd",
    "soo\.gd", "s2r\.co", "ouo\.io", "adf\.ly", "shorte\.st", "bc\.vc",
    "rebrand\.ly", "lnkd\.in", "buff\.ly", "bl\.ink"
]

# Regex to detect links/usernames/suspicious domains
PATTERN = rf'(?im)(?:https?://|www\.|t\.me/|telegram\.dog/|\w+\.({"|".join(SUSPICIOUS_DOMAINS)}))\S+|@[a-z0-9_]{5,32}\b'

@Client.on_message(filters.all)
async def handle_all_messages(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None
    user_name = message.from_user.first_name if message.from_user else "Unknown"
    text = message.text or message.caption or ""

    # Skip service messages and bot messages
    if not user_id or message.from_user.is_bot:
        return

    # =========================
    # Check if user is admin/owner
    # =========================
    try:
        member = await client.get_chat_member(chat_id, user_id)
        is_admin_or_owner = member.status in ("administrator", "creator")
    except Exception:
        is_admin_or_owner = False

    # =========================
    # 1. Detect spam links/usernames
    # =========================
    if re.search(PATTERN, text):
        if not is_admin_or_owner:  # delete only if NOT admin/owner
            try:
                await message.delete()
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await message.delete()
            print(f"🗑 Deleted spam link from {user_name} (ID: {user_id})")
            return
        else:
            print(f"✅ Skipped spam link from admin/owner {user_name} (ID: {user_id})")

    # =========================
    # 2. Detect forwarded spam
    # =========================
    if message.forward_date or message.forward_from or message.forward_from_chat:
        has_buttons = bool(message.reply_markup and message.reply_markup.inline_keyboard)
        has_spam_text = any(
            word in text.lower()
            for word in ["click", "baby", "clothes", "offer", "deal", "win"]
        )

        if re.search(PATTERN, text) or has_buttons or has_spam_text:
            if not is_admin_or_owner:  # delete only if NOT admin/owner
                try:
                    await message.delete()
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await message.delete()
                print(f"🗑 Deleted forwarded spam from {user_name} (ID: {user_id})")
                return
            else:
                print(f"✅ Skipped forwarded spam from admin/owner {user_name} (ID: {user_id})")

    # =========================
    # 3. Auto-delete regular messages (only in group, if /settime is used)
    # =========================
    if message.chat.type in ("group", "supergroup"):
        delay = get_delete_time(chat_id)
        if delay:
            await delete_user_message(message, delay)
