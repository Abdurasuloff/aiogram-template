from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import Config


class UserFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message, config: Config) -> bool:
        for channel in config.tg_bot.force_channels:
                check_member = await obj.bot.get_chat_member(channel, obj.from_user.id)
                if check_member.status not in ["member", "creator"]:
                    return False
        else:
            return True
