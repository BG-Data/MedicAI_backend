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
    # DATABASE_NAME = config("DATABASE_NAME", default="", cast=str)
    # DATABASE_URL = config(
    #     "DATABASE_URL", default="", cast=str
    # ) + DATABASE_NAME or "sqlite:///" + os.path.join(basedir, "test.db")
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # CRIPTOCODE = config("CRIPTOCODE", cast=str, default="teste")
    # SECRET_KEY = config("SECRET_KEY", cast=str, default="teste")
    # ALGORITHM = config("ALGORITHM", cast=str, default="HS256")
    # DEV_PSWD = config("DEV_PSWD", cast=str, default="teste")
    # MERCADO_PAGO_ACCESS_TOKEN = config(
    #     "MERCADO_PAGO_ACCESS_TOKEN", cast=str, default=""
    # )
    # PORT = config("PORT", default=5000, cast=int)
    # UVICORN_WORKERS = config("UVICORN_WORKERS", default=1, cast=int)
    # JWT_ACCESS_TOKEN_EXPIRES = config("JWT_ACCESS_TOKEN_EXPIRES", default=1, cast=int)

    # RELOAD = config("RELOAD", default=True, cast=bool)
    # AWS_ACCESS_KEY = config("AWS_ACCESS_KEY", cast=str)
    # AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", cast=str)
    # AWS_REGION = config("AWS_REGION", cast=str)
    # AWS_BUCKET_NAME = config("AWS_BUCKET_NAME", cast=str)
    # AWS_BUCKET_FOLDER = config("AWS_BUCKET_FOLDER", cast=str)

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
