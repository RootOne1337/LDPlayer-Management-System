# 🔐 LDPlayer Management System - API Guide

## Overview

This API provides JWT-based authentication and role-based access control (RBAC) for managing LDPlayer emulators across multiple workstations.

**Base URL:** `http://localhost:8001`  
**API Docs:** http://localhost:8001/docs  
**Authentication:** JWT Bearer tokens required (except `/health` and `/api/auth/login`)

---

## 🚀 Quick Start

### 1. Login to get JWT token

```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. Use token in subsequent requests

```bash
curl -X GET "http://localhost:8001/api/status" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 👥 Default Users

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | ADMIN | Full access (user management, all operations) |
| `operator` | `operator123` | OPERATOR | Manage emulators, workstations, operations |
| `viewer` | `viewer123` | VIEWER | Read-only access |

---

## 📚 Authentication Endpoints

### Login
**POST** `/api/auth/login`

Get JWT tokens using username and password.

**Request Body:** (form-data)
```
username: admin
password: admin123
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### Refresh Token
**POST** `/api/auth/refresh`

Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "YOUR_REFRESH_TOKEN"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### Get Current User
**GET** `/api/auth/me`

Get information about currently authenticated user.

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:**
```json
{
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "System Administrator",
  "role": "admin",
  "disabled": false,
  "created_at": "2025-01-17T10:00:00",
  "last_login": "2025-01-17T12:30:00"
}
```

---

### Logout
**POST** `/api/auth/logout`

Invalidate current access token.

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 👨‍💼 User Management (ADMIN only)

### List Users
**GET** `/api/auth/users`

Get list of all users.

**Headers:**
```
Authorization: Bearer ADMIN_ACCESS_TOKEN
```

**Response:**
```json
[
  {
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "System Administrator",
    "role": "admin",
    "disabled": false,
    "created_at": "2025-01-17T10:00:00",
    "last_login": "2025-01-17T12:30:00"
  }
]
```

---

### Register User
**POST** `/api/auth/register`

Create new user account.

**Headers:**
```
Authorization: Bearer ADMIN_ACCESS_TOKEN
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "New User",
  "password": "SecurePassword123!",
  "role": "operator"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User 'newuser' registered successfully",
  "data": {
    "username": "newuser",
    "role": "operator"
  }
}
```

---

### Delete User
**DELETE** `/api/auth/users/{username}`

Delete user account.

**Headers:**
```
Authorization: Bearer ADMIN_ACCESS_TOKEN
```

**Response:**
```json
{
  "success": true,
  "message": "User 'username' deleted successfully"
}
```

**Note:** Cannot delete yourself.

---

### Update User Role
**PUT** `/api/auth/users/{username}/role`

Change user's role.

**Headers:**
```
Authorization: Bearer ADMIN_ACCESS_TOKEN
```

**Request Body:**
```json
{
  "role": "operator"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User 'username' role updated to 'operator'"
}
```

**Note:** Cannot change your own role.

---

### Disable User
**POST** `/api/auth/users/{username}/disable`

Disable or enable user account.

**Headers:**
```
Authorization: Bearer ADMIN_ACCESS_TOKEN
```

**Request Body:**
```json
{
  "disabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "User 'username' has been disabled"
}
```

**Note:** Cannot disable yourself.

---

## 🖥️ Workstation Management

### List Workstations
**GET** `/api/workstations`

Get list of all registered workstations.

**Requires:** Any authenticated user  
**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:**
```json
[
  {
    "id": "ws_001",
    "name": "Workstation 1",
    "ip_address": "192.168.1.101",
    "status": "online",
    "emulators": [...]
  }
]
```

---

### Add Workstation
**POST** `/api/workstations`

Add new workstation.

**Requires:** OPERATOR or ADMIN  
**Headers:**
```
Authorization: Bearer OPERATOR_OR_ADMIN_TOKEN
```

**Request Body:**
```json
{
  "id": "ws_005",
  "name": "New Workstation",
  "ip_address": "192.168.1.105",
  "username": "administrator",
  "password": "workstation_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Рабочая станция New Workstation добавлена",
  "data": {
    "workstation_id": "ws_005"
  }
}
```

---

### Get Workstation Details
**GET** `/api/workstations/{workstation_id}`

Get detailed information about a workstation.

**Requires:** Any authenticated user  
**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### Test Connection
**POST** `/api/workstations/{workstation_id}/test-connection`

Test connectivity to a workstation.

**Requires:** Any authenticated user  
**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## 🎮 Emulator Management

### List Emulators
**GET** `/api/workstations/{workstation_id}/emulators`

Get list of emulators on specific workstation.

**Requires:** Any authenticated user  
**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### Create Emulator
**POST** `/api/emulators`

Create new emulator on a workstation.

**Requires:** OPERATOR or ADMIN  
**Headers:**
```
Authorization: Bearer OPERATOR_OR_ADMIN_TOKEN
```

**Request Body:**
```json
{
  "workstation_id": "ws_001",
  "name": "Test Emulator",
  "config": {
    "android_version": "9.0",
    "screen_size": "1280x720",
    "cpu_cores": 2,
    "memory_mb": 2048
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Операция создания эмулятора 'Test Emulator' поставлена в очередь",
  "data": {
    "operation_id": "op_12345",
    "emulator_name": "Test Emulator",
    "workstation_id": "ws_001"
  }
}
```

---

### Start Emulator
**POST** `/api/emulators/{emulator_id}/start`

Start an emulator.

**Requires:** OPERATOR or ADMIN  
**Headers:**
```
Authorization: Bearer OPERATOR_OR_ADMIN_TOKEN
```

---

### Stop Emulator
**POST** `/api/emulators/{emulator_id}/stop`

Stop a running emulator.

**Requires:** OPERATOR or ADMIN  
**Headers:**
```
Authorization: Bearer OPERATOR_OR_ADMIN_TOKEN
```

---

### Delete Emulator
**DELETE** `/api/emulators/{emulator_id}`

Delete an emulator.

**Requires:** OPERATOR or ADMIN  
**Headers:**
```
Authorization: Bearer OPERATOR_OR_ADMIN_TOKEN
```

---

## 📊 Operations Management

### List Operations
**GET** `/api/operations`

Get list of active operations.

**Requires:** Any authenticated user  
**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### Get Operation Details
**GET** `/api/operations/{operation_id}`

Get detailed information about an operation.

**Requires:** Any authenticated user  
**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### Cancel Operation
**POST** `/api/operations/{operation_id}/cancel`

Cancel a pending or running operation.

**Requires:** OPERATOR or ADMIN  
**Headers:**
```
Authorization: Bearer OPERATOR_OR_ADMIN_TOKEN
```

---

## 🏥 System Endpoints

### Health Check
**GET** `/api/health`

Check if API is running.

**No authentication required**

**Response:**
```json
{
  "success": true,
  "message": "Сервер работает нормально",
  "data": {
    "status": "healthy"
  }
}
```

---

### Server Status
**GET** `/api/status`

Get detailed server status.

**Requires:** Any authenticated user  
**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:**
```json
{
  "status": "running",
  "version": "1.0.0",
  "uptime": "2:30:15",
  "connected_workstations": 3,
  "total_emulators": 12,
  "active_operations": 2,
  "timestamp": "2025-01-17T12:30:00"
}
```

---

## 🔒 Security Best Practices

### Token Management
- **Access tokens** expire in 30 minutes - use refresh tokens to get new ones
- **Refresh tokens** expire in 7 days - user must login again after that
- Store tokens securely (never in localStorage, use httpOnly cookies in production)
- Always use HTTPS in production

### Password Requirements
- Minimum 8 characters
- No specific complexity requirements (bcrypt provides security)
- Change default passwords immediately

### Rate Limiting
- Consider implementing rate limiting for login endpoint
- Monitor failed login attempts

### Environment Security
- Keep `.env` file secure and never commit to git
- Use strong random JWT_SECRET_KEY (64+ characters)
- Rotate secrets regularly

---

## 📝 Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- **200** OK - Success
- **201** Created - Resource created
- **400** Bad Request - Invalid input
- **401** Unauthorized - Missing or invalid token
- **403** Forbidden - Insufficient permissions
- **404** Not Found - Resource doesn't exist
- **500** Internal Server Error - Server error

---

## 🧪 Testing

### Run API Tests
```bash
cd Server
pytest tests/test_auth.py -v  # JWT authentication tests (44 tests)
pytest tests/ -v               # All tests (68 tests)
```

### Interactive API Documentation
Visit http://localhost:8001/docs for Swagger UI with:
- Try it out functionality
- Schema documentation
- Authentication support

---

## 📞 Support

- **API Issues:** Check server logs in `Server/logs/`
- **Authentication:** Verify JWT_SECRET_KEY in `.env`
- **Permissions:** Check user role with `/api/auth/me`
- **Documentation:** Full docs at http://localhost:8001/docs

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-17  
**Status:** Production Ready ✅
