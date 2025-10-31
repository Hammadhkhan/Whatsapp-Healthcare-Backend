<div align="center">

# 🏥 Healthcare WhatsApp Chatbot

### AI-Powered Healthcare Assistant via WhatsApp Business API

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [Security](#-security)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 About

A sophisticated, production-ready WhatsApp chatbot that provides instant healthcare information, symptom analysis, and medical guidance in multiple languages. Built for **Smart India Hackathon 2025 (SIH-25049)** to improve healthcare accessibility in rural and semi-urban areas.

### 🌟 Why This Project?

- **Healthcare Gap**: 65% of rural India lacks easy access to healthcare information
- **Language Barrier**: Multi-language support (Hindi, English, Tamil, Telugu, etc.)
- **24/7 Availability**: Instant responses for health queries and emergencies
- **Privacy First**: HIPAA-compliant data handling with no personal data logging

---

## ✨ Key Features

### 🤖 AI-Powered Health Services
- **Symptom Checker**: Intelligent analysis with ML-based recommendations
- **Medicine Information**: Comprehensive drug database with usage guidelines
- **Emergency Detection**: Automatic detection and escalation of critical situations
- **Hospital Locator**: Find nearby healthcare facilities with real-time data

### 💬 Communication Features
- **Multi-Language Support**: 11+ Indian languages with automatic detection
- **WhatsApp Integration**: Seamless WhatsApp Business API integration
- **SMS Alerts**: Twilio-powered emergency notifications
- **Broadcast System**: Admin alerts for health advisories and tips

### 🔒 Security & Compliance
- **Secure Authentication**: Header-based API keys with constant-time comparison
- **No PII Logging**: Privacy-focused design with masked sensitive data
- **Environment-based Config**: Zero hardcoded secrets
- **Rate Limiting**: Protection against abuse and DoS attacks

### 📊 Admin Dashboard
- **Broadcast Alerts**: Send health tips and emergency notifications
- **Analytics**: Track usage, engagement, and health trends
- **User Management**: Monitor conversations and user interactions
- **System Health**: Real-time monitoring and logging

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  WhatsApp User  │────▶│ WhatsApp Cloud   │────▶│  FastAPI Server │
│                 │     │      API         │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                        ┌──────────────────────────────────┼──────────────────┐
                        │                                  │                  │
                ┌───────▼────────┐       ┌────────────────▼───────┐  ┌──────▼────────┐
                │                │       │                        │  │               │
                │   ML Models    │       │      Database          │  │ External APIs │
                │   - NLP        │       │   - User Sessions      │  │ - Hospital DB │
                │   - Symptom AI │       │   - Health Records     │  │ - Medicine DB │
                │                │       │                        │  │               │
                └────────────────┘       └────────────────────────┘  └───────────────┘
```

### Technology Stack

- **Backend**: FastAPI 0.104+, Python 3.8+
- **Async HTTP**: httpx for non-blocking operations
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ML/NLP**: Custom symptom checker, language detection
- **Messaging**: WhatsApp Business API, Twilio SMS
- **Deployment**: Docker, Kubernetes, Cloud-ready

---

## 📦 Prerequisites

- **Python**: 3.8 or higher
- **WhatsApp Business Account**: [Meta Developer Account](https://developers.facebook.com/)
- **Twilio Account** (optional): For SMS alerts
- **SSL Certificate**: Required for production webhook

### System Requirements
- RAM: Minimum 4GB (8GB recommended)
- Storage: 10GB free space
- OS: Linux/Ubuntu (recommended), macOS, Windows

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/Hammadhkhan/Whatsapp-Healthcare-Backend.git
cd Whatsapp-Healthcare-Backend
```

### 2. Create Virtual Environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate Secure Keys

```bash
# Generate SECRET_KEY (minimum 32 characters)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate ADMIN_API_KEY (minimum 32 characters)
python -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(32))"
```

---

## ⚙️ Configuration

### 1. Create `.env` File

```bash
cp .env.example .env
```

### 2. Configure Environment Variables

```env
# WhatsApp Configuration (REQUIRED)
WHATSAPP_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_secure_verify_token_min_32_chars
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id

# Security (REQUIRED - Use generated keys from above)
SECRET_KEY=your-generated-secret-key-32-chars
ADMIN_API_KEY=your-generated-admin-api-key-32-chars

# Admin Configuration (Comma-separated with country code)
ADMIN_PHONE_NUMBERS=911234567890,919876543210

# Twilio Configuration (Optional - for SMS)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_SMS_NUMBER=your_twilio_number
TWILIO_VERIFY_TOKEN=your_twilio_verify_token

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
EMERGENCY_NUMBER=112  # Change based on region (911 for US)

# Test Configuration (Development only)
TEST_PHONE_NUMBER=
```

### 3. WhatsApp Business API Setup

1. Create a Meta Developer account at [developers.facebook.com](https://developers.facebook.com/)
2. Create a new app and add WhatsApp product
3. Get your **Access Token** and **Phone Number ID** from the dashboard
4. Configure webhook URL: `https://yourdomain.com/webhook`
5. Set **Verify Token** (same as in `.env`)
6. Subscribe to webhook fields: `messages`, `messaging_postbacks`

---

## 💻 Usage

### Development Server

```bash
uvicorn app.main:app --reload --port 5000 --host 0.0.0.0
```

### Production Server

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000
```

### Docker

```bash
# Build image
docker build -t healthcare-bot .

# Run container
docker run -d \
  --name healthcare-bot \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  healthcare-bot
```

### Verify Installation

```bash
curl http://localhost:5000/
# Expected: {"status": "healthy", "message": "Healthcare WhatsApp Bot API"}
```

---

## 📡 API Endpoints

### Public Endpoints (No Auth)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API health check |
| `/webhook` | GET | WhatsApp webhook verification |
| `/webhook` | POST | Receive WhatsApp messages |
| `/api/health` | GET | Service status |
| `/admin/health` | GET | Admin service health |

### Protected Endpoints (Require `X-API-Key` Header)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/broadcast` | POST | Send broadcast alert |
| `/admin/emergency` | POST | Send emergency alert |
| `/admin/health-tip` | POST | Send health tip |
| `/admin/stats` | GET | Get usage statistics |

### Example API Call

```bash
# Send Broadcast Alert
curl -X POST http://localhost:5000/admin/broadcast \
  -H "X-API-Key: YOUR_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "🚨 Health Alert: Dengue cases rising. Use mosquito repellent.",
    "alert_type": "emergency",
    "priority": "high"
  }'
```

### Interactive API Documentation

- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

---

## 🚢 Deployment

### Deploy to Heroku

```bash
heroku create healthcare-whatsapp-bot
heroku config:set WHATSAPP_TOKEN=your_token
heroku config:set ADMIN_API_KEY=your_key
git push heroku main
```

### Deploy to AWS EC2

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update && sudo apt install -y python3-pip nginx supervisor

# Clone and setup
git clone https://github.com/Hammadhkhan/Whatsapp-Healthcare-Backend.git
cd Whatsapp-Healthcare-Backend
pip3 install -r requirements.txt

# Configure Nginx and Supervisor
sudo cp deployment/nginx.conf /etc/nginx/sites-available/healthcare-bot
sudo cp deployment/supervisor.conf /etc/supervisor/conf.d/healthcare-bot.conf
sudo systemctl restart nginx supervisor
```

### Deploy with Docker Compose

```bash
docker-compose up -d
```

---

## 🔐 Security

### Security Best Practices Implemented

✅ **No Hardcoded Secrets**: All credentials in environment variables  
✅ **Constant-Time Comparison**: Prevents timing attacks on API keys  
✅ **Header-Based Auth**: API keys in `X-API-Key` header (not query params)  
✅ **PII Protection**: No logging of phone numbers or message content  
✅ **Rate Limiting**: 30 requests/minute default (configurable)  
✅ **Input Validation**: Pydantic models for all inputs  
✅ **HTTPS Required**: Production webhook must use SSL  

### Security Checklist

- [ ] Generate strong random keys (32+ characters)
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS for webhook URL
- [ ] Rotate API keys every 90 days
- [ ] Enable rate limiting
- [ ] Monitor logs for suspicious activity
- [ ] Regular security audits

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_api.py -v
```

### Test WhatsApp Webhook

```bash
# Test webhook verification
curl "http://localhost:5000/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=test123"

# Expected: test123
```

### Test Admin Endpoints

```bash
python send_alert.py
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Webhook Verification Failed
```
Error: Verification failed
Solution: Ensure VERIFY_TOKEN in .env matches Meta dashboard
```

#### 2. Token Expired
```
Error: Session has expired
Solution: Generate new access token from Meta Developer Dashboard
```

#### 3. Database Connection Error
```
Error: Cannot connect to database
Solution: Check DATABASE_URL and ensure database server is running
```

#### 4. Import Error
```
Error: No module named 'app'
Solution: Ensure you're in project root and virtual environment is activated
```

### Debug Mode

Enable detailed logging:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Logs Location

- Application logs: `logs/app.log`
- Error logs: Console output with `DEBUG=True`

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
black app/ tests/
flake8 app/ tests/

# Run security checks
bandit -r app/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Smart India Hackathon 2025** for problem statement SIH-25049
- **Meta** for WhatsApp Business API
- **FastAPI** team for the excellent framework
- **Contributors** who helped improve this project

### Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Twilio](https://www.twilio.com/) - SMS notifications
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp) - Messaging platform

---

## 📞 Contact & Support

- **Project Maintainer**: Hammad Khan
- **GitHub**: [@Hammadhkhan](https://github.com/Hammadhkhan)
- **Issues**: [GitHub Issues](https://github.com/Hammadhkhan/Whatsapp-Healthcare-Backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Hammadhkhan/Whatsapp-Healthcare-Backend/discussions)

---

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: ✅ Production Ready
- **Last Updated**: November 2025
- **Maintenance**: Actively Maintained

---

## 🗺️ Roadmap

- [x] WhatsApp Business API integration
- [x] Multi-language support (11+ languages)
- [x] Symptom checker with ML
- [x] Emergency detection and alerts
- [x] Admin broadcast system
- [ ] Voice message support
- [ ] Image-based diagnosis (future)
- [ ] Integration with government health APIs
- [ ] Mobile app companion

---

<div align="center">

### ⭐ Star this repo if you find it helpful!

Made with ❤️ for better healthcare accessibility

**[Back to Top](#-healthcare-whatsapp-chatbot)**

</div>

