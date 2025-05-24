"""
Main FastAPI application for ECHO Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from typing import Dict, Any

from config.settings import settings
from api.routes import agents, messages, evolution, auth, style, i18n, audio, behaviors, learning
from services.database import init_db
from services.agent_manager import AgentManager
from agents.evolution_engine import EvolutionEngine

# Initialize managers
agent_manager = AgentManager()
evolution_engine = EvolutionEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🔊 Starting ECHO Backend...")
    print("🧠 Initializing cognitive systems...")
    await init_db()
    await agent_manager.initialize_agents()
    await agent_manager.start_reactive_behaviors()
    print("✅ ECHO is ready to amplify your voice!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await agent_manager.stop_reactive_behaviors()
    await agent_manager.shutdown()
    print("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="ECHO Backend - Your voice, amplified with intelligence",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(evolution.router, prefix="/api/evolution", tags=["evolution"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(style.router, prefix="/api/style", tags=["style"])
app.include_router(i18n.router, prefix="/api/i18n", tags=["internationalization"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(behaviors.router, prefix="/api/behaviors", tags=["behaviors"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ECHO API",
        "tagline": "Your voice, amplified with intelligence",
        "version": "0.1.0",
        "status": "operational",
        "agents": await agent_manager.get_agent_status()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "agents": len(agent_manager.agents),
        "evolution_enabled": True
    }

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    return {
        "total_messages_processed": await agent_manager.get_total_messages(),
        "active_agents": len(agent_manager.agents),
        "evolution_cycles": evolution_engine.get_statistics()["total_evolutions"],
        "learning_progress": await agent_manager.get_learning_stats()
    }

@app.post("/api/process")
async def process_message(data: Dict[str, Any]):
    """Process incoming message through appropriate agent"""
    try:
        # Extract message details
        message = data.get("message", "")
        platform = data.get("platform", "generic")
        context = data.get("context", {})
        
        # Route to appropriate agent
        result = await agent_manager.process_message(
            message=message,
            platform=platform,
            context=context
        )
        
        # Log for evolution
        await evolution_engine.analyze_interaction({
            "id": result.get("id"),
            "message": message,
            "response": result.get("response"),
            "success": result.get("success", True),
            "duration_ms": result.get("duration_ms", 0)
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    try:
        # Add to active connections
        agent_manager.add_websocket(websocket)
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process through agent
            result = await agent_manager.process_realtime(data)
            
            # Send response
            await websocket.send_json(result)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        agent_manager.remove_websocket(websocket)

@app.exception_handler(Exception)
async def global_exception_handler(_, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )