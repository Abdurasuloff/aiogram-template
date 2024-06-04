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
    use_redis: bool
    redis_url: str
    redis_host: str
    redis_port: str
    redis_password: str

    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = env.list("ADMINS")
        force_channels = env.list("FORCE_CHANNELS")
        use_redis = env.bool("USE_REDIS", default=False)
        redis_url = env.str("REDIS_URL", default=None)
        redis_host = env.str("REDIS_HOST", default=None)
        redis_port = env.int("REDIS_PORT", default=None)
        redis_password = env.str("REDIS_PASSWORD", default=None)

        return TgBot(
            token=token,
            admin_ids=admin_ids,
            force_channels=force_channels,
            use_redis=use_redis,
            redis_url=redis_url,
            redis_host=redis_host,
            redis_port=redis_port,
            redis_password=redis_password
        )


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
