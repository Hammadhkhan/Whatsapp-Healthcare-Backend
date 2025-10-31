import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # WhatsApp Configuration (NO DEFAULTS - must be set via environment)
    whatsapp_token: str = ""
    phone_number_id: str = ""
    verify_token: str = ""  # No hardcoded default
    whatsapp_business_account_id: str = ""
    
    # Twilio Configuration (NO DEFAULTS)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_sms_number: str = ""
    twilio_verify_token: str = ""  # No hardcoded default
    
    # Database Configuration
    database_url: str = "sqlite:///./healthcare.db"
    
    # Security (NO DEFAULTS - fail if not set in production)
    secret_key: str = ""
    admin_api_key: str = ""  # New: for admin endpoints
    
    # Admin Configuration
    admin_phone_numbers: str = ""
    
    # API Keys (Optional external services)
    google_maps_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    translation_api_key: Optional[str] = None
    
    # App Settings
    debug: bool = False  # Changed from True to False
    log_level: str = "INFO"
    max_conversation_history: int = 20
    session_timeout_minutes: int = 30
    rate_limit_per_minute: int = 30
    
    # ML Model Settings
    use_gpu: bool = False
    model_cache_dir: str = "./models"
    confidence_threshold: float = 0.7
    
    # External APIs
    hospital_api_url: Optional[str] = None
    medicine_db_api_url: Optional[str] = None
    government_health_api: Optional[str] = None
    data_gov_api_key: str = ""
    data_gov_base_url: str = ""
    
    # Emergency Configuration
    emergency_number: str = "112"  # Universal emergency number, configurable by region
    
    # Test Configuration (for development only)
    test_phone_number: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def _validate_security(self):
        """Validate security settings"""
        if not self.debug:
            # Production validation
            if not self.secret_key or len(self.secret_key) < 32:
                raise ValueError(
                    "Security Error: SECRET_KEY must be set to a secure random value (≥32 chars) in production!"
                )
            
            if not self.admin_api_key or len(self.admin_api_key) < 32:
                raise ValueError(
                    "Security Error: ADMIN_API_KEY must be set to a secure random value (≥32 chars) in production!"
                )
            
            if not self.whatsapp_token:
                raise ValueError("Security Error: WHATSAPP_TOKEN must be set in production!")
            
            if not self.verify_token:
                raise ValueError("Security Error: VERIFY_TOKEN must be set in production!")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_security()

# Initialize settings
settings = Settings()
