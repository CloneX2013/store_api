class BaseException(Exception):
    message: str = "Internal Server Error"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message


class NotFoundException(BaseException):
    message = "Not Found"

class BaseException(Exception):
    """Base exception class for the application."""
    message: str = "Internal Server Error"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message

class NotFoundError(BaseException):
    """Exception for data not found."""
    message = "Not Found"

class InsertionError(BaseException):
    """Exception for data insertion errors."""
    message = "Error while inserting data"
