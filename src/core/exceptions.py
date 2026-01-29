class AppError(Exception):
    """Base exception for the AI Call Agent application."""
    def __init__(self, message: str, service_name: str = "Unknown"):
        super().__init__(message)
        self.service_name = service_name
        self.message = message

class TransientError(AppError):
    """Errors that are temporary and may succeed on retry."""
    pass

class PermanentError(AppError):
    """Errors that are final and should not be retried."""
    pass

# Transient Errors
class ServiceTimeoutError(TransientError):
    """Request to the service timed out."""
    pass

class ServiceUnavailableError(TransientError):
    """Service returned 503 or is otherwise unavailable."""
    pass

class NetworkError(TransientError):
    """General network failure."""
    pass

# Permanent Errors
class AuthenticationError(PermanentError):
    """Invalid credentials or unauthorized (401)."""
    pass

class InvalidPayloadError(PermanentError):
    """Bad request or invalid data (400)."""
    pass

class QuotaExceededError(PermanentError):
    """Service quota reached."""
    pass

class ResourceNotFoundError(PermanentError):
    """Requested resource does not exist (404)."""
    pass
