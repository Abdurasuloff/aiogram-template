from dataclasses import dataclass

from environs import Env

SOCIAL_MEDIA = ["instagram", 'tik tok', 'telegram']


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: list[int]
    force_channels: list



    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = env.list("ADMINS")
        force_channels = env.list("FORCE_CHANNELS")
        return TgBot(
            token=token,
            admin_ids=admin_ids,
            force_channels=force_channels)


@dataclass
class Miscellaneous:

    other_params: str = None


@dataclass
class Config:

    tg_bot: TgBot
    misc: Miscellaneous


def load_config(path: str = None) -> Config:
    # Create an Env object.
    # The Env object will be used to read environment variables.
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
        misc=Miscellaneous(),
    )
