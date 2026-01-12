import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth_routes, task_routes
from app.core.exceptions import (
    TaskFlowException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    ConflictError
)
from app.core.logging import setup_logging, logger
from app.core.config import settings
from app.core.openapi import custom_openapi
from app.api import attachment_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan for startup/shutdown events"""
    setup_logging()
    logger.info("TaskFlow Backend Service starting up...")
    logger.info(f"Environment: {settings.environment}")
    yield
    logger.info("TaskFlow Backend Service shutting down...")


app = FastAPI(
    title="TaskFlow",
    description="Backend service for TaskFlow - Internal engineering platform for task management",
    version="1.0.0",
    lifespan=lifespan,
)

app.openapi = lambda: custom_openapi(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "local" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(TaskFlowException)
async def taskflow_exception_handler(request: Request, exc: TaskFlowException):
    """Handle custom TaskFlow exceptions"""
    logger.error(
        f"TaskFlowException: {exc.error_code} - {exc.detail} - Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.exception(
        f"Unhandled exception: {str(exc)} - Path: {request.url.path}",
        exc_info=exc
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses"""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'Unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Add process time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TaskFlow Backend",
        "version": "1.0.0"
    }


# Include routers
app.include_router(auth_routes.router)
app.include_router(task_routes.router)
app.include_router(attachment_routes.router)
