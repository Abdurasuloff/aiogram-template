from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class YesNoCallBackData(CallbackData, prefix="yes_no"):
    yes: bool


class ConfirmAdCallBackData(CallbackData, prefix="confirm"):
    confirm: bool


def yes_no_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text=f"➕ Qo'shish", callback_data=YesNoCallBackData(yes=True))
    keyboard.button(text=f"📥 Tugatish", callback_data=YesNoCallBackData(yes=False))

    return keyboard.as_markup()


def confirm_ad_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="✅ Ha", callback_data=ConfirmAdCallBackData(confirm=True).pack())
    keyboard.button(text="❌ Yo'q", callback_data=ConfirmAdCallBackData(confirm=False).pack())

    return keyboard.as_markup()


async def channels_keyboard(bot: Bot, channels):
    keyboard = InlineKeyboardBuilder()

    for ch in channels:
        chat = await bot.get_chat(chat_id=ch)
        link = await chat.create_invite_link()
        keyboard.button(text=chat.title, url=link.invite_link)

    return keyboard.as_markup()
