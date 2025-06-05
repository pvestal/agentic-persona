"""
Health check API endpoints
Monitor system health and component status
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.database.connection import db_manager, get_async_db
from backend.schemas.common import HealthResponse
from backend.utils.privacy_shield import privacy_shield

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """Get system health status"""
    services = {}
    
    # Database health
    db_health = await db_manager.health_check()
    services["database"] = db_health
    
    # Privacy shield status
    services["privacy_shield"] = {
        "status": "healthy" if privacy_shield.enabled else "disabled",
        "statistics": privacy_shield.get_statistics()
    }
    
    # Redis health (if available)
    try:
        from backend.auth.security import security_manager
        if security_manager.redis_client:
            await security_manager.redis_client.ping()
            services["redis"] = {"status": "healthy"}
        else:
            services["redis"] = {"status": "unavailable"}
    except Exception as e:
        services["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # Overall status
    all_healthy = all(
        service.get("status") in ["healthy", "disabled"] 
        for service in services.values()
    )
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services=services
    )


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_async_db)):
    """Kubernetes readiness probe"""
    try:
        # Check database connection
        db_health = await db_manager.health_check()
        if db_health["status"] != "healthy":
            return {"status": "not_ready", "reason": "database_unhealthy"}, 503
        
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}, 503


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}