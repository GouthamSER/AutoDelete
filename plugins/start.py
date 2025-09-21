import os
import sys
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pyrogram.errors import MessageNotModified, MessageDeleteForbidden
from info import ADMINS  # List of admin user IDs


# =========================
# /start command
# =========================
@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user = message.from_user.first_name or "User"
    user_id = message.from_user.id
    chat = message.chat

    is_admin = user_id in ADMINS  # check if user is an authorized admin

    if chat.type == enums.ChatType.PRIVATE:
        # Private chat welcome text
        text = (
            f"👋 Hello, **{user}**!\n\n"
            "I'm an Auto-Delete Bot for Telegram groups.\n"
            "I automatically delete messages after a configured time.\n\n"
            "🔧 **Steps to get started:**\n"
            "1. Add me to your group.\n"
            "2. Grant me admin rights with delete permission.\n"
            "3. Use `/settime` to set the auto-delete delay.\n\n"
        )

        if is_admin:
            text += "🛠️ You are an **authorized admin**. You can also use `/restart` or open settings below."
        else:
            text += "ℹ️ You are a **normal member**. Only admins can configure the bot."

        # Show settings button to everyone (popup for non-admins handled in callback)
        reply_buttons = [
            [InlineKeyboardButton("📚 Help", callback_data="help")],
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{client.me.username}?startgroup=true")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
        ]

        await message.reply(
            text=text,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(reply_buttons)
        )

    else:  # If /start is used inside a group
        if is_admin:
            await message.reply(
                "✅ **Bot is active in this group.**\n"
                "You are an admin, so you can use `/settime` and `/restart`.\n",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.reply(
                "✅ **Bot is active in this group.**\n"
                "Only admins can configure auto-delete settings.\n"
                "You can still use `/start` in private chat to learn more.",
                parse_mode=enums.ParseMode.MARKDOWN
            )


# =========================
# Callback query handler
# =========================
@Client.on_callback_query()
async def callback_query_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    msg = callback_query.message
    user_id = callback_query.from_user.id

    await callback_query.answer()  # acknowledge button click

    try:
        if data == "help":
            await msg.edit_text(
                text=(
                    "📚 **Help Menu**\n\n"
                    "`/settime 30s` – Auto-delete messages after 30 seconds\n"
                    "`/settime 5m` – Delete after 5 minutes\n"
                    "`/settime 1hr` – Delete after 1 hour\n\n"
                    "`/deltime` – Show current delete timer in the group\n\n"
                    "⚙️ Only admin IDs listed in `ADMINS` can use these commands.\n"
                    "Supported formats: `10s`, `2m`, `1hr`"
                ),
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="back")]
                ])
            )

        elif data == "back":
            user = callback_query.from_user.first_name or "User"
            reply_buttons = [
                [InlineKeyboardButton("📚 Help", callback_data="help")],
                [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{client.me.username}?startgroup=true")],
                [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
            ]

            await msg.edit_text(
                text=(
                    f"👋 Hello, **{user}**!\n\n"
                    "I'm an Auto-Delete Bot for Telegram groups.\n"
                    "I automatically delete messages after a configured time.\n\n"
                    "🔧 **Steps to get started:**\n"
                    "1. Add me to your group.\n"
                    "2. Grant me admin rights with delete permission.\n"
                    "3. Use `/settime` to set the auto-delete delay.\n\n"
                    "Only specific user IDs (set in `ADMINS`) can configure me."
                ),
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(reply_buttons)
            )

        elif data == "settings":
            if user_id not in ADMINS:
                # Popup alert for non-admins
                await callback_query.answer("🚫 Only admins can access settings.", show_alert=True)
                return

            await msg.edit_text(
                text="⚙️ **Bot Settings Panel**\nChoose an option below:",
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏱ Set Auto-Delete Time", callback_data="set_time")],
                    [InlineKeyboardButton("📄 View Current Settings", callback_data="view_settings")],
                    [InlineKeyboardButton("🔁 Restart Bot", callback_data="restart_bot")],
                    [InlineKeyboardButton("❌ Close", callback_data="close")]
                ])
            )

        elif data == "set_time":
            await msg.edit_text(
                "⏱ To set auto-delete time, send a command like:\n\n"
                "`/settime 30s`\n`/settime 2m`\n`/settime 1hr`",
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="settings")]
                ])
            )

        elif data == "view_settings":
            current_setting = "30s"  # Replace with dynamic value later
            await msg.edit_text(
                f"📄 **Current Auto-Delete Time**: `{current_setting}`",
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="settings")]
                ])
            )

        elif data == "restart_bot":
            if user_id not in ADMINS:
                await callback_query.answer("🚫 Only admins can restart the bot.", show_alert=True)
                return

            await msg.edit_text("🔁 Restarting...")
            await asyncio.sleep(2)
            os.execl(sys.executable, sys.executable, *sys.argv)

        elif data == "close":
            try:
                await msg.delete()
            except MessageDeleteForbidden:
                pass

    except MessageNotModified:
        pass


# =========================
# /restart command
# =========================
@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart_command(bot, message: Message):
    msg = await bot.send_message("**𝖡𝗈𝗍 𝖨𝗌 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀...🪄**", chat_id=message.chat.id)
    await asyncio.sleep(3)
    try:
        await msg.edit_text("**✅ Bot Restarted Successfully! Ready to work.**")
    except MessageNotModified:
        pass
    os.execl(sys.executable, sys.executable, *sys.argv)


# Deny restart for non-admins
@Client.on_message(filters.command("restart") & ~filters.user(ADMINS))
async def restart_denied(client: Client, message: Message):
    await message.reply("❌ You are not authorized to restart the bot.")
