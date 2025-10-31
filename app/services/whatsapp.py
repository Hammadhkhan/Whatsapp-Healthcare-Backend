import httpx
import logging
from typing import Dict, Any, Optional
import json

from app.config import settings

logger = logging.getLogger(__name__)


class UnifiedWhatsAppService:
    """Unified WhatsApp service with async HTTP client"""
    
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/v17.0/{settings.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {settings.whatsapp_token}",
            "Content-Type": "application/json"
        }
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
    
    async def ensure_client(self):
        """Ensure async client is initialized"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message to WhatsApp user"""
        await self.ensure_client()
        
        # Format phone number to E.164 (with + prefix)
        to_clean = to.replace("+", "").replace(" ", "").replace("-", "")
        if not to_clean.startswith("+"):
            to_clean = f"+{to_clean}"
        
        # Log with masked number
        masked = f"***{to_clean[-4:]}" if len(to_clean) > 4 else "****"
        logger.info(f"📤 Sending message to {masked}")
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_clean,
            "type": "text",
            "text": {"body": text}
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload
            )
            
            # Accept all 2xx status codes
            if 200 <= response.status_code < 300:
                logger.info("✅ Message sent successfully")
                return response.json()
            else:
                error_data = response.json()
                logger.error(f"❌ Failed to send message: {error_data}")
                return {"success": False, "error": error_data}
                
        except Exception as e:
            logger.error(f"Exception sending message: {e}")
            return {"success": False, "error": str(e)}
    
    def parse_webhook_message(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse webhook message with proper validation"""
        try:
            logger.info("📥 Parsing webhook")
            
            entries = data.get('entry', [])
            if not entries:
                logger.info("No entries found in webhook")
                return None
            
            entry = entries[0]
            changes = entry.get('changes', [])
            if not changes:
                logger.info("No changes found")
                return None
            
            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            contacts = value.get('contacts', [])
            
            if not messages:
                logger.info("No messages found")
                return None
            
            message = messages[0]
            contact = contacts[0] if contacts else {}
            
            # Extract safe metadata only
            return {
                'message_id': message.get('id'),
                'from': message.get('from'),
                'timestamp': message.get('timestamp'),
                'type': message.get('type'),
                'text': message.get('text', {}).get('body', ''),
                'contact_name': contact.get('profile', {}).get('name', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Error parsing webhook: {e}", exc_info=True)
            return None
    
    async def close(self):
        """Close async HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None


# Lazy initialization
_whatsapp_service: Optional[UnifiedWhatsAppService] = None


def get_whatsapp_service() -> UnifiedWhatsAppService:
    """Get or create the WhatsApp service instance (lazy initialization)"""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = UnifiedWhatsAppService()
    return _whatsapp_service
'''

# Save file list
file_list = list(files.keys())
print("✅ Generated all updated code files:")
for i, filename in enumerate(file_list, 1):
    lines = len(files[filename].splitlines())
    print(f"{i}. {filename} ({lines} lines)")

print(f"\n📊 Total files: {len(files)}")
print("=" * 60)
