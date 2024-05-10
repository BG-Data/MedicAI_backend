class OriginalException(Exception):
    """
    Base Exception customized

    Attributes:
        message (str): The error message describing the reason for the exception.

    Methods:
        __init__(self, message): Initializes the BaseException exception with the given message.
        __str__(self): Returns the error message as a string representation of the exception.
    """

    def __init__(self, message):
        self.message = message.replace("  ", "").replace("\n", "")
        super().__init__()

    def __str__(self):
        return self.message


class UserNotFound(OriginalException):
    pass


class PhotoInvalid(OriginalException):
    pass


class AwsInsertionFailed(OriginalException):
    pass


class AlreadyExist(OriginalException):
    pass


class NotFound(OriginalException):
    pass


class AuthenticationError(OriginalException):
    pass


class InvalidPassword(OriginalException):
    pass


class AlreadyConnected(OriginalException):
    pass


class Forbidden(OriginalException):
    pass


class InvalidResultType(OriginalException):
    pass
