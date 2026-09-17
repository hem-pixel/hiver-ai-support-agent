from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.models import HealthResponse
from app.routes.analyze import router as analyze_router

app = FastAPI(
    title="Hiver AI Support Agent API",
    description="Backend API for customer support message classification, resolution retrieval, and automated routing decisions.",
    version="0.1.0"
)

# Enable CORS for local development with the Vite React frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation error handler providing clear error messages."""
    errors = []
    for err in exc.errors():
        location = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": location,
            "message": err.get("msg")
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": errors
        }
    )



@app.get(
    "/api/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    tags=["System"]
)
async def health_check() -> HealthResponse:
    """Service health check endpoint."""
    return HealthResponse(
        status="ok",
        service="hiver-ai-support-agent"
    )


# Include modular route handlers
app.include_router(analyze_router)
