from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.errors.app_errors import AppError
from src.configs.database import engine, Base
from src.configs.settings import settings

# APIs routes
from src.modules.auth.routes import router as auth_router
from src.modules.instructor.courses.routes import router as courses_router

# Create FastAPI app
app = FastAPI(title="Youverse Task APIs",
              description="Video Streaming Platform API",
              version="1.0.0",
              docs_url="/docs",
              redoc_url="/redoc")

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
