import asyncio
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Get credentials from environment (NO DEFAULTS)
WHATSAPP_TOKEN = ""
PHONE_NUMBER_ID = ""
VERIFY_TOKEN = ""
TEST_NUMBER = ""


async def main():
    """Main debug function"""
    load_dotenv()  # Load .env at start
    
    global WHATSAPP_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN, TEST_NUMBER
    
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
    PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
    TEST_NUMBER = os.getenv("TEST_PHONE_NUMBER", "")
    
    print("🚑 Running WhatsApp Debugging Script")
    print("=" * 50)
    
    # Validate required environment variables
    if not WHATSAPP_TOKEN:
        print("❌ Error: WHATSAPP_TOKEN not set in .env file")
        return
    
    if not PHONE_NUMBER_ID:
        print("❌ Error: WHATSAPP_PHONE_NUMBER_ID not set in .env file")
        return
    
    if not TEST_NUMBER:
        print("❌ Error: TEST_PHONE_NUMBER not set in .env file")
        return
    
    # Log token presence (not the actual token)
    print(f"✓ Token present: {bool(WHATSAPP_TOKEN)}")
    print(f"✓ Phone ID present: {bool(PHONE_NUMBER_ID)}")
    print(f"✓ Test number configured: {bool(TEST_NUMBER)}")
    
    # Test message payload
    test_payload = {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "text",
        "text": {
            "body": "🚑 Test message from Healthcare Bot"
        }
    }
    
    print("\n✅ Configuration validated")
    print(f"Ready to send test message to: ***{TEST_NUMBER[-4:]}")
    print("\n" + "=" * 50)
    print("To actually send test message, run:")
    print("python -m app.services.whatsapp")


if __name__ == "__main__":
    asyncio.run(main())
