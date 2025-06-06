import os
import tgcrypto
import sys
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from info import ADMINS  # Make sure ADMINS is a list of admin user IDs

# /start command
@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user = message.from_user.first_name or "User"
    user_id = message.from_user.id
    chat = message.chat

    is_admin = user_id in ADMINS

    if chat.type == enums.ChatType.PRIVATE:
        text = (
            f"👋 Hello, **{user}**!\n\n"
            "I'm an Auto-Delete Bot built for Telegram groups.\n"
            "I automatically delete messages after a configured time.\n\n"
            "🔧 **Steps to get started:**\n"
            "1. Add me to your group.\n"
            "2. Grant me admin rights with delete permission.\n"
            "3. Use `/settime` to set the auto-delete delay.\n\n"
            "Only specific user IDs (set in `ADMINS`) can configure me."
        )

        if is_admin:
            text += "\n\n🛠️ As an admin, you can also use `/restart` or open settings below."

        reply_buttons = [
            [InlineKeyboardButton("📚 Help", callback_data="help")],
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{client.me.username}?startgroup=true")]
        ]

        if is_admin:
            reply_buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])

        await message.reply(
            text=text,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(reply_buttons)
        )
    else:
        await message.reply(
            text=(
                "✅ **Bot is active in this group.**\n"
                "Use `/settime` to configure the auto-delete time.\n"
                "Only authorized admins (set in `ADMINS`) can configure it."
            ),
            parse_mode=enums.ParseMode.MARKDOWN
        )

# Callback query handler
@Client.on_callback_query()
async def callback_query_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    msg = callback_query.message
    user_id = callback_query.from_user.id

    if data == "help":
        await callback_query.answer()
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
        await callback_query.answer()
        user = msg.from_user.first_name if msg.from_user else "User"
        reply_buttons = [
            [InlineKeyboardButton("📚 Help", callback_data="help")],
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{client.me.username}?startgroup=true")]
        ]
        if user_id in ADMINS:
            reply_buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="settings")])

        await msg.edit_text(
            text=(
                f"👋 Hello, **{user}**!\n\n"
                "I'm an Auto-Delete Bot built for Telegram groups.\n"
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
            await callback_query.answer("🚫 Only admins can access settings.", show_alert=True)
            return

        await callback_query.answer()
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
        await callback_query.answer()
        await msg.edit_text(
            "⏱ To set auto-delete time, send a command like:\n\n"
            "`/settime 30s`\n`/settime 2m`\n`/settime 1hr`",
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    elif data == "view_settings":
        # Replace this placeholder with real config data
        current_setting = "30s"  # Example value
        await callback_query.answer()
        await msg.edit_text(
            f"📄 **Current Auto-Delete Time**: `{current_setting}`",
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ])
        )

    elif data == "restart_bot":
        await callback_query.answer("Restarting bot...")
        await msg.edit("🔁 Restarting...")
        await asyncio.sleep(2)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif data == "close":
        await callback_query.answer("Settings closed.")
        await msg.delete()


# /restart command (admin only)
@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart_command(bot, message: Message):
    msg = await bot.send_message("**𝖡𝗈𝗍 𝖨𝗌 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀...🪄**", chat_id=message.chat.id)
    await asyncio.sleep(3)
    await msg.edit("**𝖡𝗈𝗍 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 ! 𝖱𝖾𝖺𝖽𝗒 𝖳𝗈 𝖬𝗈𝗏𝖾 𝖮𝗇 💯**")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Deny restart for non-admins
@Client.on_message(filters.command("restart") & ~filters.user(ADMINS))
async def restart_denied(client: Client, message: Message):
    await message.reply("❌ You are not authorized to restart the bot.")
