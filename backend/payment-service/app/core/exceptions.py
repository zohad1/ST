from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class PaymentServiceException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class PaymentProcessingError(PaymentServiceException):
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(message, 402)

class InsufficientFundsError(PaymentServiceException):
    def __init__(self, message: str = "Insufficient funds for payout"):
        super().__init__(message, 402)

class InvalidPaymentMethodError(PaymentServiceException):
    def __init__(self, message: str = "Invalid payment method"):
        super().__init__(message, 400)

def add_exception_handlers(app):
    @app.exception_handler(PaymentServiceException)
    async def payment_service_exception_handler(request: Request, exc: PaymentServiceException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error", "errors": exc.errors()}
        )
