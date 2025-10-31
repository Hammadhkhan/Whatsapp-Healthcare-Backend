import asyncio
import httpx
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def send_alert_with_retry(
    url: str,
    method: str = "POST",
    max_retries: int = 3,
    timeout: int = 120,
    headers: dict = None,
    json_data: dict = None
):
    """Send alert with retry logic and increased timeout"""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            
            async with httpx.AsyncClient() as client:
                if method == "POST":
                    response = await client.post(
                        url,
                        headers=headers,
                        json=json_data,
                        timeout=timeout
                    )
                else:
                    response = await client.get(
                        url,
                        headers=headers,
                        timeout=timeout
                    )
            
            return response
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)


async def send_broadcast_alert():
    """Send broadcast emergency alert"""
    print("🚨 EMERGENCY BROADCAST ALERT TEST")
    print("=" * 50)
    
    message = f"""🚨 HEALTH EMERGENCY ALERT

⚠️  Dengue Outbreak Reported in Your Area

📋 SYMPTOMS TO WATCH FOR:
• High fever
• Severe headache
• Joint pain
• Rash
• Nausea
• Vomiting

🛡️  PREVENTIVE MEASURES:
• Use mosquito repellent
• Wear long sleeves
• Eliminate standing water
• Seek medical care early

📞 EMERGENCY CONTACTS:
• Emergency Services: {settings.emergency_number}
• Government Helpline: 1075

💡 This is an official health advisory."""
    
    url = "http://localhost:5000/admin/broadcast"
    headers = {
        "X-API-Key": settings.admin_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "message": message,
        "alert_type": "emergency",
        "priority": "high"
    }
    
    try:
        print("Sending alert (this may take 30-60 seconds)...")
        response = await send_alert_with_retry(
            url,
            method="POST",
            timeout=120,
            headers=headers,
            json_data=payload
        )
        
        if response.status_code == 200:
            print("✅ Alert sent successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Alert failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def send_health_tip():
    """Send daily health tip"""
    print("\n💡 HEALTH TIP TEST")
    print("=" * 50)
    
    message = f"""💡 DAILY HEALTH TIP

✅ HEALTHY LIFESTYLE TIPS:
• Stay hydrated (8 glasses daily)
• Exercise 30 minutes daily
• Eat balanced nutritious meals
• Get 7-8 hours quality sleep

📞 Emergency: Call {settings.emergency_number}

💡 This is general guidance - individual needs vary!"""
    
    url = "http://localhost:5000/admin/broadcast"
    headers = {
        "X-API-Key": settings.admin_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "message": message,
        "alert_type": "health_tip",
        "priority": "normal"
    }
    
    try:
        print("Sending health tip...")
        response = await send_alert_with_retry(
            url,
            method="POST",
            timeout=120,
            headers=headers,
            json_data=payload
        )
        
        if response.status_code == 200:
            print("✅ Health tip sent successfully!")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main test function"""
    try:
        await send_broadcast_alert()
        await asyncio.sleep(2)
        await send_health_tip()
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
