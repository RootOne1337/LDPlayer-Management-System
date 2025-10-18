# Installation Guide

Complete step-by-step installation instructions for LDPlayer Management System.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Options](#installation-options)
3. [Manual Installation](#manual-installation)
4. [Docker Installation](#docker-installation)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS:** Windows 10+ or Linux (Ubuntu 20.04+)
- **Python:** 3.9 or higher
- **Node.js:** 16.0 or higher (for frontend)
- **RAM:** 4GB minimum
- **Disk Space:** 2GB free space

### Recommended Requirements
- **OS:** Windows 11 or Ubuntu 22.04
- **Python:** 3.11 or higher
- **Node.js:** 18.0 or higher
- **RAM:** 8GB or more
- **Disk Space:** 5GB free space

### LDPlayer Requirements
- **LDPlayer:** Version 9.0 or higher
- **Windows API:** For WinRM compatibility (Windows 10+)

## Installation Options

### Quick Start (Docker) - 5 minutes
Best for production deployments and isolated environments.
See [Docker Installation](#docker-installation) section.

### Development Setup - 15 minutes
Best for local development and testing.
See [Manual Installation](#manual-installation) section.

### Production Setup - 30 minutes
For deploying to production servers.
See [Configuration](#configuration) section.

## Manual Installation

### Step 1: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/yourusername/LDPlayerManagementSystem.git
cd LDPlayerManagementSystem

# Or download ZIP
# Extract to your desired location
# cd LDPlayerManagementSystem
```

### Step 2: Python Backend Setup

#### Create Virtual Environment

**Windows:**
```bash
cd Server
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd Server
python3 -m venv venv
source venv/bin/activate
```

#### Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed')"
```

#### Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Use your preferred text editor
```

**`.env` File Template:**
```env
# Server Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8001

# Security
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_EXPIRATION=86400

# Database
DATABASE_URL=sqlite:///./ldplayer.db

# LDPlayer
LDPLAYER_EXECUTABLE=/Program Files/LDPlayer/LDPlayer.exe

# SMTP (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Logging
LOG_FILE=logs/app.log
```

### Step 3: Frontend Setup

#### Install Node.js Dependencies

```bash
cd ../frontend
npm install
```

#### Build Frontend

**Development:**
```bash
npm run dev
```

**Production:**
```bash
npm run build
```

### Step 4: Start the Application

#### Terminal 1: Backend Server

```bash
cd Server

# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start server
python -m uvicorn src.core.server:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 2: Frontend Development (optional)

```bash
cd frontend
npm run dev
```

#### Access the Application

- **API Server:** http://localhost:8001
- **API Documentation:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc
- **Frontend:** http://localhost:8001/static/index.html (production build)

## Docker Installation

### Prerequisites
- Docker installed (https://www.docker.com/products/docker-desktop)
- Docker Compose (usually included with Docker Desktop)

### Build Docker Image

```bash
# Build image
docker build -t ldplayer-system:latest .

# Or use docker-compose
docker-compose build
```

### Run with Docker

#### Option 1: Docker Run

```bash
docker run -d \
  --name ldplayer-system \
  -p 8001:8001 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  ldplayer-system:latest
```

#### Option 2: Docker Compose

```bash
# Create docker-compose.override.yml (optional)
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Verify Docker Installation

```bash
# Check container status
docker ps -a | grep ldplayer-system

# View logs
docker logs ldplayer-system

# Access running container
docker exec -it ldplayer-system bash
```

## Configuration

### Application Settings

Edit `.env` or use environment variables:

```bash
# Server Configuration
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=WARNING
export PORT=8000

# Security
export JWT_SECRET="$(openssl rand -hex 32)"
export JWT_EXPIRATION=86400

# Database
export DATABASE_URL=sqlite:////data/ldplayer.db
```

### Database Initialization

The database automatically initializes on first run. To manually initialize:

```bash
cd Server
python -c "from src.core import models; models.init_db()"
```

### SSL/HTTPS Configuration

For production, configure SSL:

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Or use Let's Encrypt for production
# See DEPLOYMENT.md for details
```

## Verification

### Test Backend

```bash
# Run health check
curl http://localhost:8001/api/health

# Expected output:
# {
#   "status": "running",
#   "version": "1.0.0",
#   "timestamp": "2025-10-19T10:30:00Z"
# }
```

### Run Test Suite

```bash
cd Server
python -m pytest tests/ -v

# Expected output:
# ===================== 125 passed in 40.72s =======================
```

### Login Test

```bash
# Request token
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in requests
TOKEN="your-token-here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/status
```

## Troubleshooting

### Python Issues

**Issue:** `python: command not found`
```bash
# Solution: Use python3
python3 --version
python3 -m venv venv
```

**Issue:** `ModuleNotFoundError`
```bash
# Solution: Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
```

### Node.js Issues

**Issue:** `npm: command not found`
```bash
# Solution: Install Node.js from https://nodejs.org/
node --version
npm --version
```

**Issue:** `port 3000 already in use`
```bash
# Solution: Use different port
npm run dev -- --port 3001
```

### Port Conflicts

**Check port usage:**
```bash
# Windows
netstat -ano | findstr :8001

# macOS/Linux
lsof -i :8001

# Kill process (if needed)
# Windows: taskkill /PID <PID> /F
# macOS/Linux: kill -9 <PID>
```

### Database Issues

**Reset database:**
```bash
# Remove old database
rm Server/ldplayer.db

# Restart server (will recreate)
python -m uvicorn src.core.server:app --reload
```

### Docker Issues

**Container won't start:**
```bash
# Check logs
docker logs ldplayer-system

# Rebuild image
docker build --no-cache -t ldplayer-system:latest .
```

**Permission denied:**
```bash
# Fix permissions (Linux)
sudo chown -R $USER:$USER .
docker run --user $(id -u) ...
```

### Network Issues

**Firewall configuration:**
```bash
# Windows Defender
# Allow through: LDPlayer Management System

# Linux firewall
sudo ufw allow 8001/tcp
sudo ufw allow 3000/tcp
```

**CORS Issues:**
```bash
# Edit .env
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8001"]
```

## Next Steps

1. Read [CONFIGURATION.md](./CONFIGURATION.md) for detailed settings
2. See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for API usage
3. Check [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup
4. Review [CONTRIBUTING.md](./CONTRIBUTING.md) for development

## Support

- **Documentation:** See `docs/` folder
- **Issues:** Report on GitHub Issues
- **Discussions:** Use GitHub Discussions
- **Email:** support@your-domain.com

---

**Successful installation?** Great! Start using the application by accessing http://localhost:8001
