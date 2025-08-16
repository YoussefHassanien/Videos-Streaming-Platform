from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.errors.app_errors import AppError
from src.configs.database import engine, Base
from src.configs.settings import settings
from src.configs.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# APIs routes
from src.modules.auth.routes import router as auth_router
from src.modules.instructor.courses.routes import router as courses_router
from src.modules.student.subscription.routes import router as subscription_router

# Create FastAPI app
app = FastAPI(title="Youverse Task APIs",
              description="Video Streaming Platform API",
              version="1.0.0",
              docs_url="/docs",
              redoc_url="/redoc")

# Add the limiter to the app's state. This makes it accessible in request dependencies.
app.state.limiter = limiter

# Add a global exception handler for rate limit exceeded errors.
app.add_exception_handler(RateLimitExceeded,
                          _rate_limit_exceeded_handler)  # type: ignore

if (settings.environment == 'development'):

    @app.on_event("startup")
    async def create_tables():
        Base.metadata.create_all(bind=engine)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Exception handler for custom AppError
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code,
                        content={
                            "message": exc.detail,
                        })


# App routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

app.include_router(courses_router, prefix="/api/v1/course", tags=["Courses"])

app.include_router(subscription_router,
                   prefix="/api/v1/subscribe",
                   tags=["Subscriptions"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Youverse Task APIs",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "youverse-apis"}
