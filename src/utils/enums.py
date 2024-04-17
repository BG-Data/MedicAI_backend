from enum import Enum


class UserType(str, Enum):
    cliente = "cliente"


class UserTypePrivileged(str, Enum):
    admin = "admin"
