class TraderError(Exception):
    pass


class AuthenticationError(TraderError):
    """Failed to authenticate."""


class ApiError(TraderError):
    """Request returned 450."""


class ApiServerError(TraderError):
    """Request returned 500."""


class ConnectionError(TraderError):
    """A connection error occurred."""


class UnknownError(TraderError):
    """An unknown error."""


class Timeout(TraderError):
    """The request timed out."""
