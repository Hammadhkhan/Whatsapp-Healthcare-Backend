import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import secrets
from typing import Optional
from datetime import datetime, timezone

from app.config import settings

# Ensure logs directory exists BEFORE logging setup
Path('logs').mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Import services after logging is configured
from app.services.admin_alert_service import AdminAlertService
from app.services.whatsapp import UnifiedWhatsAppService, get_whatsapp_service
from app.services.message_processor import MessageProcessor

# Global service instances
admin_alert_service: Optional[AdminAlertService] = None
message_processor: Optional[MessageProcessor] = None


# ============================================================================
# AUTHENTICATION HELPERS
# ============================================================================

def verify_admin_api_key(api_key: str) -> bool:
    """Verify admin API key using constant-time comparison."""
    if not api_key or not settings.admin_api_key:
        return False
    return secrets.compare_digest(api_key, settings.admin_api_key)


async def admin_auth_required(x_api_key: str = Header(None, alias="X-API-Key")):
    """FastAPI dependency for admin authentication via header."""
    if not verify_admin_api_key(x_api_key):
        logger.warning("❌ Failed admin authentication attempt")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return True


# ============================================================================
# APPLICATION LIFESPAN (STARTUP/SHUTDOWN)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    global admin_alert_service, message_processor
    
    logger.info("🚀 Starting Healthcare WhatsApp Bot...")
    
    try:
        # Initialize admin alert service
        admin_alert_service = AdminAlertService()
        await admin_alert_service.initialize()
        logger.info("✅ [ALERTS] Admin alert service initialized")
        
        # Initialize message processor
        message_processor = MessageProcessor()
        logger.info("✅ [PROCESSOR] Message processor initialized")
        
        # Initialize WhatsApp service (lazy initialization on first use)
        logger.info("✅ [WHATSAPP] WhatsApp service ready (lazy init)")
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Healthcare WhatsApp Bot...")
    try:
        if admin_alert_service:
            await admin_alert_service.shutdown()
            logger.info("✅ [SHUTDOWN] Admin alert service closed")
        
        # Close WhatsApp service if initialized
        whatsapp_service = get_whatsapp_service()
        if whatsapp_service and whatsapp_service.client:
            await whatsapp_service.close()
            logger.info("✅ [SHUTDOWN] WhatsApp service closed")
            
        logger.info("✅ All services shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Healthcare WhatsApp Bot",
    description="AI-powered healthcare chatbot for WhatsApp",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "message": "Healthcare WhatsApp Bot API",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/api/health",
            "admin": "/admin/*"
        }
    }


# ============================================================================
# WEBHOOK ENDPOINTS (WhatsApp)
# ============================================================================

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verify WhatsApp webhook - called by Meta during setup"""
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")
    
    # Log without exposing tokens
    logger.info(f"📋 Webhook verification request - Mode: {hub_mode}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.verify_token:
        logger.info("✅ Webhook verified successfully")
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        logger.error("❌ Webhook verification failed: token mismatch")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def receive_message(request: Request):
    """Receive and process WhatsApp messages"""
    try:
        data = await request.json()
        
        # Log metadata only, not full payload (PII risk)
        entry_count = len(data.get('entry', []))
        logger.info(f"📥 Received webhook with {entry_count} entries")
        
        # Process message using message processor
        if message_processor:
            result = await message_processor.process_webhook(data)
            return {"status": "success", "result": result}
        else:
            logger.error("Message processor not initialized")
            return {"status": "error", "message": "Service not ready"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Return 200 to prevent Meta from retrying
        return {"status": "error", "message": str(e)}


# ============================================================================
# ADMIN ENDPOINTS (Protected with API Key)
# ============================================================================

@app.post("/admin/broadcast")
async def send_broadcast_alert(
    request: Request,
    authenticated: bool = Depends(admin_auth_required)
):
    """Send broadcast alert to all users (Admin only)"""
    try:
        data = await request.json()
        message = data.get("message")
        alert_type = data.get("alert_type", "info")
        priority = data.get("priority", "normal")
        
        logger.info(f"📢 Broadcasting {alert_type} alert (Priority: {priority})")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Use admin alert service to broadcast
        if admin_alert_service:
            result = await admin_alert_service.send_broadcast(
                message=message,
                alert_type=alert_type,
                priority=priority
            )
            return {
                "status": "success",
                "message": "Broadcast alert sent successfully",
                "result": result
            }
        else:
            raise HTTPException(status_code=503, detail="Alert service not available")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending broadcast alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/emergency")
async def send_emergency_alert(
    request: Request,
    authenticated: bool = Depends(admin_auth_required)
):
    """Send emergency alert (Admin only)"""
    try:
        data = await request.json()
        message = data.get("message")
        affected_area = data.get("affected_area")
        instructions = data.get("instructions")
        
        logger.info("🚨 Sending emergency alert")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if admin_alert_service:
            result = await admin_alert_service.send_emergency_alert(
                message=message,
                affected_area=affected_area,
                instructions=instructions
            )
            return {
                "status": "success",
                "message": "Emergency alert sent successfully",
                "result": result
            }
        else:
            raise HTTPException(status_code=503, detail="Alert service not available")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending emergency alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/health-tip")
async def send_health_tip(
    request: Request,
    authenticated: bool = Depends(admin_auth_required)
):
    """Send health tip (Admin only)"""
    try:
        data = await request.json()
        message = data.get("message")
        category = data.get("category")
        
        logger.info("💡 Sending health tip")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if admin_alert_service:
            result = await admin_alert_service.send_health_tip(message, category)
            return {
                "status": "success",
                "message": "Health tip sent successfully",
                "result": result
            }
        else:
            raise HTTPException(status_code=503, detail="Alert service not available")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending health tip: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/health")
async def admin_health_check():
    """Admin service health check (No auth required)"""
    return {
        "status": "healthy",
        "service": "admin_alerts",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "admin_alert": admin_alert_service is not None,
            "message_processor": message_processor is not None
        }
    }


@app.get("/admin/stats")
async def api_stats(authenticated: bool = Depends(admin_auth_required)):
    """Get API statistics (Admin only)"""
    try:
        # TODO: Implement actual stats from database
        return {
            "status": "success",
            "stats": {
                "total_messages": 0,
                "active_users": 0,
                "total_alerts_sent": 0,
                "uptime": "N/A"
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH/STATUS ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def api_health():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "healthcare_bot_api",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url)}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# Export for use in other modules
__all__ = ['app', 'admin_auth_required', 'verify_admin_api_key']
'''
