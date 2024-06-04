from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from database.models import User
from database.orm import UserDB
from tgbot.filters.admin import AdminFilter
from tgbot.config import load_config
from tgbot.keyboards.inline import ConfirmAdCallBackData, confirm_ad_keyboard
from tgbot.keyboards.reply import admin_menu
from tgbot.misc.states import SendAdState
from tgbot.services.broadcaster import send_copy_broadcast

config = load_config(".env")

admin_router = Router()
admin_router.message.filter(AdminFilter())


# Start Command For Admins
@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.reply(f"Assalomu alaykum, {message.from_user.full_name}", reply_markup=admin_menu)

    user_info = dict(
        id=message.from_user.id,
        name=message.from_user.full_name,
        username=message.from_user.full_name,
        language=message.from_user.language_code,
    )













# ======================================ADS=========================================================

# Send AD
@admin_router.message(F.text.contains("📢 Reklama jo'natish"))
async def send_ad(message: Message, state: FSMContext):
    await message.answer("Ok, Barchaga yuborish uchun xabarni kiriting:")
    await state.set_state(SendAdState.message)


# Confirm The Ad
@admin_router.message(SendAdState.message)
async def confirm_ad(message: Message, state: FSMContext):
    await state.update_data(
        {"message_id": message.message_id,
         "chat_id": message.chat.id
         }
    )
    markup = confirm_ad_keyboard()
    await message.reply("Ushbu xabar barcha foydalanuvchilarga jo'natilsinmi?", reply_markup=markup)
    await state.set_state(SendAdState.ready)


# Send the AD
@admin_router.callback_query(SendAdState.ready, ConfirmAdCallBackData.filter())
async def send_the_ad(call: CallbackQuery, state: FSMContext, callback_data: ConfirmAdCallBackData):
    await call.answer()

    if callback_data.confirm:
        data = await state.get_data()
        message_id = data['message_id']
        chat_id = data['chat_id']
        users = await User.all()

        # markup = ad_keyboard(name="🖇 Bog'lanish", username=config.tg_bot.ad_username)
        await send_copy_broadcast(call.bot, users, message_id, chat_id, reply_markup=None)
        await call.message.edit_text("✅ Jarayon boshlandi tugagandan so'ng sizni ogohlantiramiz.", reply_markup=None)

    else:
        await call.message.edit_text("❌ Xabarni yuborish bekor qilindi.", reply_markup=None)

    await state.clear()


# Show stats
@admin_router.message(F.text.contains("📊 Statistika"))
async def stats(message: Message):
    stats = await User.stats()
    # await message.delete()
    text = "📊Statistika"
    text += f"\n\n<b>👤Foydalanuvchilar soni :</b>  {stats['users']}"
    text += f"\n<b>🖥Yaratilgan Taqdimotlar:</b> {stats['presentations']} "

    await message.answer(text)
