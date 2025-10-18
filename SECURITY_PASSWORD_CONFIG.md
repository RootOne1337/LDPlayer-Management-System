# 🔐 Password Configuration Guide

## Overview

This project uses a secure password management system that separates configuration from secrets:

- **config.json**: Contains workstation configurations with placeholder passwords
- **.env**: Contains actual encrypted passwords for development
- **Production**: Passwords loaded from environment variables or secure secret management

## Configuration Structure

### config.json (Version Control Safe ✅)

```json
{
  "workstations": [
    {
      "id": "ws_001",
      "username": "dimas",
      "password": "set_from_env",  // ← Placeholder - ACTUAL password from .env!
      ...
    }
  ]
}
```

The placeholder `"set_from_env"` tells the application to:
1. Look for environment variable: `WS_001_PASSWORD` (or `WS_002_PASSWORD`, etc.)
2. Load the actual password from `.env` file at runtime
3. Use the loaded password for workstation connection

### .env (Development Only - NOT in Git ✅)

```bash
# Development passwords (local testing only)
WS_001_PASSWORD=SecurePass123!@#
WS_002_PASSWORD=SecurePass456!@#

# Production: Use secure secret management system
# Examples:
# - AWS Secrets Manager
# - Azure Key Vault
# - Hashicorp Vault
# - Docker Secrets
```

**IMPORTANT:** `.env` file:
- ✅ Should be in `.gitignore` (not committed)
- ✅ Should have restricted file permissions (chmod 600)
- ✅ Should be backed up securely
- ❌ Should NEVER be shared in repositories or Slack

## Loading Mechanism

### Runtime Flow

```python
# In src/core/config.py

def load_config():
    # 1. Read config.json
    config = load_json("config.json")
    
    # 2. For each workstation with "set_from_env" password
    for ws in config.workstations:
        if ws.password == "set_from_env":
            # 3. Load from environment variable
            env_var = f"WS_{ws.id.upper()}_PASSWORD"
            ws.password = os.getenv(env_var)
            
            # 4. Validate password is not empty
            if not ws.password:
                raise RuntimeError(f"Missing password: {env_var}")
    
    return config
```

## Security Best Practices

### ✅ DO (Current Implementation)

1. **Separate secrets from configuration**
   - Passwords NOT in config.json ✅
   - Passwords NOT in source code ✅

2. **Use environment variables**
   - .env file for local development ✅
   - Environment variables in production ✅

3. **Validate on startup**
   - Ensure all passwords are set ✅
   - Raise errors if missing ✅

4. **Never log passwords**
   - Passwords filtered from logs ✅
   - Error messages sanitized ✅

### ❌ DON'T

1. **Hardcode passwords** in config.json or Python files
2. **Commit .env** to version control
3. **Share passwords** in messages or Slack
4. **Use weak passwords** (min 8 chars, mixed case + numbers + symbols)
5. **Log sensitive data** in debug output

## Development Setup

### Step 1: Create .env file

```bash
# Windows PowerShell
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### Step 2: Add your passwords

Edit `.env` and add your workstation credentials:

```bash
WS_001_PASSWORD=YourSecurePassword123!@#
WS_002_PASSWORD=YourOtherPassword456!@#
WS_003_PASSWORD=AnotherPassword789!@#
```

### Step 3: Verify setup

```bash
# Run server - it will validate all passwords on startup
python run_server.py

# Expected output:
# ✅ Config loaded successfully
# ✅ All workstation passwords validated
# ✅ Server running on 0.0.0.0:8001
```

## Production Deployment

### Option 1: Docker Secrets

```dockerfile
# Dockerfile
ENV WS_001_PASSWORD=${WS_001_PASSWORD}
ENV WS_002_PASSWORD=${WS_002_PASSWORD}
```

```bash
# Run container with environment variables
docker run -e WS_001_PASSWORD="secure_pass" \
           -e WS_002_PASSWORD="another_pass" \
           ldplayer-manager:latest
```

### Option 2: AWS Secrets Manager

```python
import boto3

def get_password_from_aws(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# Usage
password = get_password_from_aws('ldplayer/ws_001_password')
os.environ['WS_001_PASSWORD'] = password
```

### Option 3: Azure Key Vault

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_password_from_azure(secret_name):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://<vault-name>.vault.azure.us/", 
                         credential=credential)
    return client.get_secret(secret_name).value

# Usage
password = get_password_from_azure('ws-001-password')
os.environ['WS_001_PASSWORD'] = password
```

## Troubleshooting

### ❌ Error: "Missing password: WS_001_PASSWORD"

**Problem:** Environment variable not set

**Solution:**
```bash
# Check if .env exists
ls -la .env  # Linux/Mac
dir .env     # Windows

# Verify .env has the variable
grep WS_001_PASSWORD .env

# If missing, add it to .env
echo "WS_001_PASSWORD=your_password" >> .env
```

### ❌ Error: "Invalid workstation password"

**Problem:** Password in config.json is not "set_from_env"

**Solution:**
```bash
# Fix config.json
python -c "
import json
with open('config.json') as f:
    config = json.load(f)
for ws in config['workstations']:
    ws['password'] = 'set_from_env'
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
print('✅ Fixed!')
"
```

### ❌ Error: "Password is empty"

**Problem:** WS_XXX_PASSWORD is empty string

**Solution:**
```bash
# Make sure password is not empty
# .env format: KEY=VALUE (no quotes needed, no spaces)
WS_001_PASSWORD=SecurePass123!@#  # ✅ Good
WS_001_PASSWORD=""                # ❌ Bad - empty!
WS_001_PASSWORD="SecurePass123"   # ⚠️ Works, but quotes are parsed too
```

## Testing Passwords

```bash
# Test that password is loaded correctly
python -c "
from src.core.config import load_config
config = load_config()
for ws in config.workstations:
    print(f'{ws.name}: password loaded = {bool(ws.password)}')"
```

Expected output:
```
ws_001: password loaded = True
ws_002: password loaded = True
ws_003: password loaded = True
```

## Password Requirements

- **Minimum length:** 8 characters
- **Character types:** Uppercase + Lowercase + Numbers + Symbols
- **Examples:**
  - ✅ `SecurePass123!@#`
  - ✅ `Admin$Pass456`
  - ✅ `MyP@ssw0rd!`
  - ❌ `password123` (no uppercase/symbols)
  - ❌ `Pass1!` (too short)

## References

- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [12 Factor App - Store Config](https://12factor.net/config)
- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)

---

**Last Updated:** 2025-10-19 03:10 UTC
**Security Level:** 🟢 GOOD (Passwords in .env, separated from config.json)
