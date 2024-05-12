from enum import Enum


class UserType(str, Enum):
    cliente = "cliente"
    medico = "medico"


class UserTypePrivileged(str, Enum):
    admin = "admin"


class SenterType(str, Enum):
    bot = "bot"
    usuario = "usuario"
