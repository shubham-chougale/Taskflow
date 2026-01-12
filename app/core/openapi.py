from fastapi.openapi.utils import get_openapi

def custom_openapi(app):
    """
    Adds JWT Bearer auth support to Swagger
    WITHOUT using OAuth2PasswordBearer
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 🔐 Define Bearer JWT scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # 🔐 Apply globally to all endpoints
    openapi_schema["security"] = [
        {"BearerAuth": []}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
