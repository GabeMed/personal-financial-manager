class ServiceError(Exception):
    """Base class for business-rule violations raised by the service layer.

    The API layer maps each subclass to an HTTP status code (see main.py), so
    services stay independent from FastAPI.
    """

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NotFoundError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass
