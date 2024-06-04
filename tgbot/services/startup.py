import logging
from tgbot.config import load_config
from aiogram import types, Bot


async def on_startup_notify(bot: Bot, admin_id: int):
    try:
        await bot.send_message(admin_id,
                               f"Bot is started")

    except Exception as err:
        logging.exception(err)


async def set_default_commands(bot: Bot):
    await bot.set_my_commands(
        commands=[
            types.BotCommand(command="start", description="Botni ishga tushurish"),
            types.BotCommand(command="help", description="Yordam"),
        ]
    )

# async def on_startup(bot: Bot, admin_ids: list[int]):
#     await broadcaster.broadcast(bot, admin_ids, "Bot is started")
