"""
FastAPI application entry point for multi-tenant ERP system.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-tenant SaaS ERP for marketplace sellers",
    docs_url="/docs",  # Always enable docs for now (disable later in production)
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "ERP API is running",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Include routers
from app.auth.routes import router as auth_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

# TODO: Add more routers as modules are developed
# from app.workspaces.routes import router as workspaces_router
# app.include_router(workspaces_router, prefix="/api/v1/workspaces", tags=["Workspaces"])
