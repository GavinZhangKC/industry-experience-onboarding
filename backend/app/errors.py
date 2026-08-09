"""One error type per failure mode, each mapping to a status code and a stable
machine-readable code.

BE-F5: "return consistent error responses". The frontend switches on
error.code, never on the message text, so wording can change freely.
"""


class AppError(Exception):
    status_code = 500
    code = "internal_error"
    message = "Something went wrong on our side."

    def __init__(self, message: str | None = None, *, details: dict | None = None):
        super().__init__(message or self.message)
        self.message = message or self.message
        self.details = details or {}


class InvalidRequest(AppError):
    status_code = 422
    code = "invalid_request"
    message = "The request data was not valid."


class OutOfServiceArea(AppError):
    status_code = 422
    code = "out_of_service_area"
    message = "That location is outside the area this app covers."


class NoRoutesFound(AppError):
    status_code = 404
    code = "no_routes_found"
    message = "No walking routes were found between those two points."


class UpstreamError(AppError):
    status_code = 502
    code = "upstream_error"
    message = "The mapping service did not respond correctly. Please try again."


class DataUnavailable(AppError):
    status_code = 503
    code = "data_unavailable"
    message = "Reference data could not be loaded."


class RateLimited(AppError):
    status_code = 429
    code = "rate_limited"
    message = "Too many requests. Please slow down and try again shortly."
