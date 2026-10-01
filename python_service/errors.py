class APIError(Exception):
    """Service error with a public HTTP status and message."""

    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
