from environs import Env
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str


@dataclass
class WebHookData:
    web_host: str
    web_path: str
    web_secret: str
    web_url: str
    web_ssl_cert: str
    web_ssl_priv: str


@dataclass
class RedisData:
    url: str
    port: int


@dataclass
class cookie:
    cookie: str


@dataclass
class Config:
    tg_bot: TgBot
    webhook_data: WebHookData
    redis_data: RedisData
    cookie: cookie


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(token=env('BOT_TOKEN')),
        webhook_data=WebHookData(
            web_host=env('WEB_SERVER_HOST'),
            web_path=env('WEBHOOK_PATH'),
            web_secret=env('WEBHOOK_SECRET'),
            web_url=env('BASE_WEBHOOK_URL'),
            web_ssl_cert=env('WEBHOOK_SSL_CERT'),
            web_ssl_priv=env('WEBHOOK_SSL_PRIV')
        ),
        redis_data=RedisData(
            url=env('REDIS_URL'),
            port=env('REDIS_PORT')
        ),
        cookie=cookie(
            cookie=env('COOKIE')
        )
    )
