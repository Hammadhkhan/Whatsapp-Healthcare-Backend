import logging
from typing import Dict, Any, Optional
from app.services.whatsapp import get_whatsapp_service
from app.config import settings

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Process incoming WhatsApp messages"""
    
    def __init__(self):
        self.whatsapp_service = get_whatsapp_service()
        logger.info("Message processor initialized")
    
    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook data from WhatsApp"""
        try:
            # Parse message
            message_data = self.whatsapp_service.parse_webhook_message(data)
            
            if not message_data:
                logger.info("No processable message found")
                return {"status": "no_message"}
            
            from_number = message_data.get('from')
            message_text = message_data.get('text', '')
            
            logger.info(f"📨 Processing message: {message_text[:50]}...")
            
            # Process message and generate response
            response_text = await self.generate_response(message_text, from_number)
            
            # Send response
            if response_text:
                result = await self.whatsapp_service.send_text_message(from_number, response_text)
                return {"status": "processed", "sent": result}
            
            return {"status": "processed", "sent": False}
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def generate_response(self, message: str, from_number: str) -> str:
        """Generate response to user message"""
        try:
            message_lower = message.lower().strip()
            
            # Greeting
            if any(greet in message_lower for greet in ['hi', 'hello', 'hey', 'namaste']):
                return """👋 Hello! Welcome to Healthcare Assistant.

I can help you with:
• Symptom checking
• Health information
• Emergency guidance
• Find hospitals
• Medicine information

How can I assist you today?"""
            
            # Emergency detection
            elif any(word in message_lower for word in ['emergency', 'urgent', 'critical', 'help']):
                return f"""🚨 EMERGENCY ASSISTANCE

If this is a medical emergency:
📞 Call {settings.emergency_number} immediately

For urgent care:
• Stay calm
• Note symptoms
• Contact nearest hospital

Reply with your symptoms for immediate guidance."""
            
            # Symptom checking
            elif any(word in message_lower for word in ['symptom', 'pain', 'fever', 'cough', 'headache']):
                return """🏥 SYMPTOM CHECKER

Please describe your symptoms in detail:
• When did they start?
• How severe are they? (1-10)
• Any other symptoms?

I'll provide guidance based on your symptoms.

⚠️ This is not a diagnosis. Seek medical care if symptoms worsen."""
            
            # Medicine info
            elif any(word in message_lower for word in ['medicine', 'medication', 'drug', 'tablet']):
                return """💊 MEDICINE INFORMATION

Please provide:
• Medicine name
• Your question about it

I'll provide information on:
• Usage instructions
• Common side effects
• Precautions

⚠️ Always consult your doctor before taking any medication."""
            
            # Hospital finder
            elif any(word in message_lower for word in ['hospital', 'clinic', 'doctor', 'nearby']):
                return """🏥 FIND HEALTHCARE FACILITIES

To find nearby hospitals/clinics:
• Share your location
• Or tell me your area/city

I'll help you find:
• Nearest hospitals
• Specialist clinics
• Emergency centers"""
            
            # Default response
            else:
                return """I'm here to help! You can ask me about:

🏥 Health symptoms
💊 Medicine information
🚨 Emergency guidance
🏥 Find hospitals
💡 Health tips

What would you like to know?"""
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error. Please try again."
