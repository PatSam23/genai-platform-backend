# JWT Authentication - Testing Guide

## ✅ Implementation Complete

JWT authentication has been successfully implemented! All chat and RAG endpoints now require authentication.

## 🔐 What Changed

### New Files
- **app/core/auth.py** - Authentication dependency with `get_current_user()`

### Updated Files
- **app/core/security.py** - Added `decode_access_token()` function
- **app/api/v1/chat.py** - Protected chat endpoints
- **app/api/v1/rag.py** - Protected RAG endpoints

### Protected Endpoints
All the following endpoints now require JWT authentication:
- ✅ POST `/api/v1/chat` - Chat completion
- ✅ POST `/api/v1/chat/stream` - Streaming chat
- ✅ POST `/api/v1/rag/query` - RAG query
- ✅ POST `/api/v1/rag/pdf/stream` - PDF streaming RAG
- ✅ POST `/api/v1/rag/ingest/pdf` - PDF ingestion
- ✅ POST `/api/v1/rag/pdf` - PDF RAG

### Public Endpoints (No Auth Required)
- ✅ POST `/api/v1/auth/register` - User registration
- ✅ POST `/api/v1/auth/login` - User login
- ✅ GET `/api/v1/health` - Health check

## 🧪 How to Test

### 1. **Restart Your Backend Server**

Stop the current server (Ctrl+C) and restart:
```bash
python run.py
```

### 2. **Open Swagger UI**

Go to: http://127.0.0.1:8000/docs

### 3. **Test Authentication Flow**

#### Step 1: Register a User
```
POST /api/v1/auth/register
email: test@example.com
password: mypassword123
```

#### Step 2: Login to Get Token
```
POST /api/v1/auth/login
email: test@example.com
password: mypassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Copy the `access_token` value!**

#### Step 3: Authorize in Swagger UI

1. Click the **"Authorize" button** 🔓 at the top of Swagger UI
2. Paste your token in the "Value" field (just the token, not "Bearer")
3. Click **"Authorize"**
4. Click **"Close"**

You should now see a 🔒 icon next to protected endpoints.

#### Step 4: Test Protected Endpoints

Now try any chat or RAG endpoint - they should work!

**Example - Chat:**
```json
{
  "prompt": "Hello, how are you?",
  "history": [],
  "context": null
}
```

### 4. **Test Authentication Failure**

#### Without Token:
- Click **"Authorize"** → **"Logout"**
- Try to call `/chat` → You'll get `401 Unauthorized`

#### With Invalid Token:
- Authorize with token: `invalid_token_123`
- Try to call `/chat` → You'll get `401 Unauthorized`

## 📝 Response Examples

### ✅ Success (with valid token):
```json
{
  "response": "I'm doing well, thank you for asking! How can I help you today?"
}
```

### ❌ Unauthorized (no token):
```json
{
  "detail": "Not authenticated"
}
```

### ❌ Invalid Token:
```json
{
  "detail": "Invalid or expired token"
}
```

## 🔍 What's Logged

Check `logs/auth.log` for authentication events:
- Token validation attempts
- User authentication success/failure
- Invalid token warnings

## 🚀 Using from Frontend/Client

### JavaScript/TypeScript Example:

```typescript
// 1. Login and get token
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'email=test@example.com&password=mypassword123'
});
const { access_token } = await loginResponse.json();

// 2. Use token for protected endpoints
const chatResponse = await fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    prompt: "Hello!",
    history: [],
    context: null
  })
});
```

### Python Example:

```python
import requests

# 1. Login
login_response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    data={'email': 'test@example.com', 'password': 'mypassword123'}
)
token = login_response.json()['access_token']

# 2. Use token
chat_response = requests.post(
    'http://localhost:8000/api/v1/chat',
    headers={'Authorization': f'Bearer {token}'},
    json={'prompt': 'Hello!', 'history': [], 'context': None}
)
```

### cURL Example:

```bash
# 1. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=test@example.com&password=mypassword123" \
  | jq -r '.access_token')

# 2. Use token
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello!","history":[],"context":null}'
```

## 🔧 Token Configuration

Token settings in `.env`:
```env
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60  # Token expires after 1 hour
```

⚠️ **Important**: Change `JWT_SECRET_KEY` to a strong random value in production!

## ✨ Benefits

- ✅ **Security**: Only authenticated users can access AI features
- ✅ **User Tracking**: Know which user made which request
- ✅ **Rate Limiting**: Can implement per-user rate limits
- ✅ **Cost Control**: Track usage per user
- ✅ **Audit Trail**: Full logging of user actions
- ✅ **Production Ready**: Industry-standard JWT authentication

## 🎯 Next Steps

Consider implementing:
1. **Token Refresh**: Implement refresh tokens for better UX
2. **Password Reset**: Add forgot password functionality
3. **Email Verification**: Verify email addresses
4. **User Profiles**: Add user profile management
5. **Rate Limiting**: Implement per-user rate limits
6. **Usage Tracking**: Track API usage per user
7. **Admin Routes**: Create admin-only endpoints
