from twilio.rest import Client
import logging
from typing import Dict, Any
import secrets

from app.config import settings

logger = logging.getLogger(__name__)


class TwilioSMSService:
    """Twilio SMS service with secure credential handling"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twilio client"""
        try:
            account_sid = settings.twilio_account_sid
            auth_token = settings.twilio_auth_token
            
            if not account_sid or not auth_token:
                raise ValueError("Twilio credentials not configured")
            
            self.client = Client(account_sid, auth_token)
            logger.info("✅ Twilio SMS service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            raise
    
    def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        """Send SMS using Twilio"""
        try:
            if not self.client:
                self._initialize_client()
            
            # Log with masked number
            masked_to = f"***{to[-4:]}" if len(to) > 4 else "****"
            logger.info(f"📱 Sending SMS to {masked_to}")
            
            message_obj = self.client.messages.create(
                body=message,
                from_=settings.twilio_sms_number,
                to=to
            )
            
            return {
                "success": True,
                "sid": message_obj.sid,
                "status": message_obj.status
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return {"success": False, "error": str(e)}
    
    def verify_webhook(self, data: Dict[str, Any]) -> bool:
        """Verify Twilio webhook using constant-time comparison"""
        try:
            verify_token = data.get('verify_token')
            expected_token = settings.twilio_verify_token
            
            if not verify_token or not expected_token:
                return False
            
            if secrets.compare_digest(verify_token, expected_token):
                logger.info("✅ Twilio webhook verification successful")
                return True
            else:
                logger.error("❌ Twilio webhook verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying webhook: {e}")
            return False
    
    def close(self):
        """Close Twilio SMS service"""
        try:
            self.client = None
            logger.info("🔌 Twilio SMS service closed")
            return {"success": True, "message": "Twilio SMS service closed"}
        except Exception as e:
            logger.error(f"Error closing Twilio SMS service: {e}")
            return {"success": False, "error": str(e)}
