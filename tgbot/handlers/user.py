from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import F
from tgbot.config import load_config
from tgbot.filters.user import UserFilter
from tgbot.keyboards.reply import main_menu

config = load_config(".env")
user_router = Router()
# user_router.message.filter(UserFilter())


# Start Command For Ordinary Users
@user_router.message(CommandStart())
async def user_start(message: Message):
    text = f"👋 Salom!"
    await message.answer(text, reply_markup=main_menu)


@user_router.message(F.text == "❌ Bekor qilish")
async def state_error(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅Chiqildi!", reply_markup=main_menu)


@user_router.message(F.text == "/help")
@user_router.message(F.text == "🆘 Yordam")
async def user_start(message: Message, state: FSMContext):
    await message.answer("Haha, no help!!")
