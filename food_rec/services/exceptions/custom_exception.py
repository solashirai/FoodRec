from typing import Optional


class CustomException(Exception):
    def __init__(self, *, message: Optional[str] = None):
        Exception.__init__(self, message)
