import os
from datetime import timedelta

from decouple import config

basedir = os.path.abspath(os.path.dirname(__file__))
import sys

from loguru import logger

from common.secrets import InfisicalClient

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="Config Settings",
    level="INFO",
)


class Config:
    ENVIRONMENT = config("ENVIRONMENT", default="test", cast=str)
    INFISICAL_TOKEN = config("INFISICAL_TOKEN")
    FLOWISE_URL = config("FLOWISE_URL", cast=str)
    FLOWISE_TOKEN = config("FLOWISE_TOKEN", cast=str)

    def __init__(self):
        if self.INFISICAL_TOKEN and self.ENVIRONMENT != "test":
            self.get_credentials()

    def get_credentials(self):
        client = InfisicalClient(self.INFISICAL_TOKEN, self.ENVIRONMENT)
        # client = InfisicalClient(token=config('INFISICAL_TOKEN'))
        # for secret in client.get_all_secrets(environment=ENVIRONMENT,
        #                                      path='/'):
        for secret_key, secret_value in client.get_secrets().items():
            if not hasattr(self, secret_key):
                setattr(self, secret_key, secret_value)
                logger.info(f"New secret add {secret_key}")


cfg = Config()
logger.info(
    f"Started {cfg.ENVIRONMENT} environment. Acessing {cfg.DATABASE_NAME} database"
)


# print(cfg)
# OBS
# Sem acesso à AWS, a senha e usuário são teste e dev respectivamente (SQLITE)
