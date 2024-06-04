import asyncio
import logging
import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder
from database.db_config import Base, engine
from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.services.startup import on_startup_notify, set_default_commands


config = load_config(".env")

def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    middleware_types = [
        ConfigMiddleware(config),
    ]

    if config.tg_bot.use_redis:
        from tgbot.middlewares.throttle_redis import ThrottlingMiddleware
        middleware_types.append(ThrottlingMiddleware(get_storage(use_redis=True).redis))

    else:
        from tgbot.middlewares.throttle import ThrottlingMiddleware
        middleware_types.append(ThrottlingMiddleware(get_storage(use_sqlite=True), ))


    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(use_sqlite: bool = False, use_redis: bool = False):

    if use_sqlite:
        from aiogram_sqlite_storage.sqlitestore import SQLStorage
        my_storage = SQLStorage('storage.db', serializing_method='pickle')
        return my_storage

    elif use_redis:
        from aiogram.fsm.storage.redis import RedisStorage
        return RedisStorage.from_url(
            config.REDIS_URL,
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )

    else:
        return MemoryStorage()


Base.metadata.create_all(bind=engine)


async def main():
    setup_logging()

    storage = get_storage(use_sqlite=True)

    # session = AiohttpSession(proxy="http://proxy.server:3128")
    # bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode="HTML" ), session=session)
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    register_global_middlewares(dp, config)

    await on_startup_notify(bot, config.tg_bot.admin_ids[0])
    await set_default_commands(bot)
    await dp.start_polling(bot)


def run():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot is stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot is stopped")
