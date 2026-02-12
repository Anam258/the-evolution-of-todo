from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.security import SecurityHeadersMiddleware
from middleware.auth_middleware import JWTAuthMiddleware
from api.auth import router as auth_router
from api.tasks import router as tasks_router
from config.auth_config import validate_startup_configuration
from database import init_db
import os
import sys
import time


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    # Validate startup configuration before creating the app
    try:
        print("Validating startup configuration...")
        validate_startup_configuration()
        print("[SUCCESS] Startup configuration validated successfully")

        # Ensure all SQLModel tables exist (CREATE TABLE IF NOT EXISTS)
        print("Syncing database schema...")
        # Import models so SQLModel registers them before create_all
        from models.user import User   # noqa: F401
        from models.task import Task   # noqa: F401
        init_db()
        print("[SUCCESS] Database schema synced")
    except ValueError as e:
        print(f"[ERROR] Startup configuration error: {e}")
        print("[INFO] Please check your .env file and ensure all required environment variables are set correctly.")
        sys.exit(1)  # Exit the application if configuration is invalid
    except Exception as e:
        print(f"[ERROR] Unexpected error during startup validation: {e}")
        print("[INFO] Please check your configuration and try again.")
        sys.exit(1)

    # Create FastAPI app
    app = FastAPI(
        title="TaskPulse AI API",
        description="TaskPulse AI — API with JWT-based authentication and user isolation",
        version="1.0.0"
    )

    # ── Middleware stack ────────────────────────────────────────────
    # FastAPI executes middleware in REVERSE registration order.
    # Register innermost first, outermost last.
    #   Execution order:  CORS  →  JWTAuth  →  SecurityHeaders  →  route
    #
    # 1. Security headers (innermost — runs closest to the route)
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. JWT auth (middle — rejects unauthenticated on protected paths)
    app.add_middleware(JWTAuthMiddleware)

    # 3. CORS (outermost — must run first so preflight never hits auth)
    # ALLOWED_ORIGINS: comma-separated list, e.g. "http://localhost:3000,https://your-app.vercel.app"
    default_origins = [
        "http://localhost:3000",
        "https://taskpulse-ai.vercel.app",
        "https://the-evolution-of-todo.onrender.com",
    ]
    raw_origins = os.getenv("ALLOWED_ORIGINS", "")
    env_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    allowed_origins = list(dict.fromkeys(env_origins + default_origins))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Access-Control-Allow-Origin"],
    )

    # Include API routers under /api/v1
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(tasks_router, prefix="/api/v1")

    @app.get("/")
    def read_root():
        """
        Root endpoint for the API.

        Returns:
            Welcome message
        """
        return {"message": "Welcome to the TaskPulse AI API"}

    @app.get("/health")
    def health_check():
        """
        Health check endpoint for the API.

        Returns:
            Health status
        """
        return {"status": "healthy", "service": "todo-api"}

    @app.get("/monitoring/health")
    def detailed_health_check():
        """
        Detailed health check endpoint with additional monitoring information.

        Returns:
            Detailed health status including dependencies
        """
        import psutil
        import os

        # Basic health status
        health_status = {
            "status": "healthy",
            "service": "todo-api",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

        # Add system resource information
        try:
            health_status["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage("/").percent,
                "uptime_seconds": time.time() - os.times()[4] if hasattr(os, 'times') else "N/A"
            }
        except Exception as e:
            # If we can't get system stats, continue without them
            health_status["system"] = {"error": "Unable to retrieve system stats", "details": str(e)}

        # Add application-specific health indicators
        try:
            # Check if the auth configuration is valid
            from config.auth_config import auth_config
            is_valid = auth_config.is_valid_secret_key()
            health_status["auth_config_valid"] = is_valid

            # Add more detailed auth status
            if is_valid:
                health_status["auth_status"] = {
                    "configured": True,
                    "secret_length": len(auth_config.get_secret_key()),
                    "validation_passed": True
                }
            else:
                health_status["auth_status"] = {
                    "configured": False,
                    "error": "Authentication configuration failed validation"
                }
        except Exception as e:
            health_status["auth_config_valid"] = False
            health_status["auth_status"] = {
                "configured": False,
                "error": f"Error checking auth config: {str(e)}"
            }

        return health_status

    @app.get("/monitoring/metrics")
    def get_metrics():
        """
        Metrics endpoint for monitoring.

        Returns:
            Application metrics
        """
        import psutil
        import os

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "active_connections": 0,  # Would be populated in a real implementation
                "requests_per_minute": 0,  # Would be populated in a real implementation
                "error_rate": 0  # Would be populated in a real implementation
            }
        }

        return metrics

    return app


# Create the application instance
app = create_app()


# If running this file directly, start the server
if __name__ == "__main__":
    import uvicorn
    from utils.port_checker import get_port_with_fallback

    # Get an available port, with fallback logic
    port = get_port_with_fallback(int(os.getenv("PORT", 8000)))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )