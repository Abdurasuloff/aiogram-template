import asyncio
import logging
from enum import Enum
from typing import Union

from aiogram import Bot
from aiogram import exceptions
from aiogram.types import InlineKeyboardMarkup

from database.models import User
from tgbot.config import load_config

config = load_config(".env")

class BRStatus(Enum):
    success = "success"
    blocked = "blocked"
    not_found = "not_found"
    others = "others"

async def send_message(
    bot: Bot,
    user_id: Union[int, str],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
) -> bool:
    """
    Safe messages sender

    :param bot: Bot instance.
    :param user_id: user id. If str - must contain only digits.
    :param text: text of the message.
    :param disable_notification: disable notification or not.
    :param reply_markup: reply markup.
    :return: success.
    """
    try:
        await bot.send_message(
            user_id,
            text,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
        )
    except exceptions.TelegramBadRequest as e:
        logging.error("Telegram server says - Bad Request: chat not found")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_message(
            bot, user_id, text, disable_notification, reply_markup
        )  # Recursive call
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcast(
    bot: Bot,
    users: list[Union[str, int]],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup = None,
) -> int:
    """
    Simple broadcaster.
    :param bot: Bot instance.
    :param users: List of users.
    :param text: Text of the message.
    :param disable_notification: Disable notification or not.
    :param reply_markup: Reply markup.
    :return: Count of messages.
    """
    count = 0
    try:
        for user_id in users:
            if await send_message(
                bot, user_id, text, disable_notification, reply_markup
            ):
                count += 1
            await asyncio.sleep(
                0.05
            )  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successful sent.")

    return count


async def send_copy(
        bot: Bot,
        user_id: Union[int, str],
        message_id: Union[int, str],
        chat_id: Union[int, str],
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup = None,
) -> BRStatus:
    """
    Safe messages sender

    :param bot: Bot instance.
    :param user_id: user id. If str - must contain only digits.
    :param text: text of the message.
    :param disable_notification: disable notification or not.
    :param reply_markup: reply markup.
    :return: success.
    """
    try:

        await bot.copy_message(user_id, chat_id, message_id, reply_markup=reply_markup)
    except exceptions.TelegramBadRequest as e:
        logging.error("Telegram server says - Bad Request: chat not found")
        return BRStatus.not_found
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
        return BRStatus.blocked
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)

        return await send_copy(
            bot, user_id, message_id, disable_notification, reply_markup=reply_markup
        )  # Recursive call

    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
        return BRStatus.others
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return BRStatus.success

    return BRStatus.others


async def send_copy_broadcast(
        bot: Bot,
        users: list[Union[User, dict]],
        message_id: list[Union[str, int]],
        chat_id: list[Union[str, int]],
        disable_notification: bool = False,
        reply_markup: InlineKeyboardMarkup = None,
) -> int:
    status_counts = dict(success=0, blocked=0, not_found=0, others=0)

    try:
        for user in users:
            status = await send_copy(
                bot, user.id, message_id, chat_id, disable_notification, reply_markup=reply_markup
            )

            if status in BRStatus:
                status_counts[status.value] += 1
            else:
                status_counts["others"] += 1

            # 20 messages per second (Limit: 30 messages per second)
            await asyncio.sleep(0.05)
    finally:
        logging.info(f"{status_counts[BRStatus.success.value]} messages successful sent.")
        text = (
            "Xabar yuborish jarayoni tugadi:\n"
            f"✅ Muvaffaqiyatli: {status_counts[BRStatus.success.value]}\n"
            f"⛔ Bloklangan: {status_counts[BRStatus.blocked.value]}\n"
            f"❓ Topilmadi: {status_counts[BRStatus.not_found.value]}\n"
            f"🔄 Boshqalar: {status_counts[BRStatus.others.value]}\n"
        )

        await bot.send_message(chat_id=int(config.tg_bot.admin_ids[0]), text=text)

    return status_counts[BRStatus.success.value]