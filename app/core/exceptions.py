from fastapi import HTTPException, status


class TaskFlowException(HTTPException):
    """Base exception for TaskFlow application"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, error_code: str = "INTERNAL_ERROR"):
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationError(TaskFlowException):
    """Raised when authentication fails"""
    def __init__(self, detail: str = "Could not validate credentials", error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED, error_code=error_code)


class AuthorizationError(TaskFlowException):
    """Raised when user lacks required permissions"""
    def __init__(self, detail: str = "Insufficient permissions", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN, error_code=error_code)


class NotFoundError(TaskFlowException):
    """Raised when a resource is not found"""
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND, error_code=error_code)


class ValidationError(TaskFlowException):
    """Raised when validation fails"""
    def __init__(self, detail: str = "Validation error", error_code: str = "VALIDATION_ERROR"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST, error_code=error_code)


class ConflictError(TaskFlowException):
    """Raised when a resource conflict occurs"""
    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT, error_code=error_code)
