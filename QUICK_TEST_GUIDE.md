# Quick Test Guide - Security Features

## 🚀 Getting Started

### 1. Start the Backend
```bash
cd genai-platform-backend
python run.py
```

### 2. Open Swagger UI
Navigate to: http://localhost:8000/docs

---

## ✉️ Test 1: Email Validation

### Valid Email ✅
```bash
POST /api/v1/auth/register
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
# Expected: 200 OK - User created
```

### Invalid Email ❌
```bash
POST /api/v1/auth/register
{
  "email": "invalid-email",
  "password": "SecurePass123!"
}
# Expected: 400 Bad Request
# Error: "Invalid email format: ..."
```

---

## 🔄 Test 2: Refresh Tokens

### Step 1: Login
```bash
POST /api/v1/auth/login
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",  ← Save this!
  "token_type": "bearer"
}
```

### Step 2: Use Refresh Token
```bash
POST /api/v1/auth/refresh
{
  "refresh_token": "eyJhbGc..."  ← Paste here
}

Response:
{
  "access_token": "eyJhbGc...",  ← New token!
  "token_type": "bearer"
}
```

---

## ⏱️ Test 3: Rate Limiting

### Step 1: Register User
```bash
POST /api/v1/auth/register
{
  "email": "ratelimit@test.com",
  "password": "SecurePass123!"
}
```

### Step 2: Try Wrong Password 5 Times
```bash
# Attempt 1
POST /api/v1/auth/login
{
  "email": "ratelimit@test.com",
  "password": "wrong1"
}
Response: "Invalid credentials. 4 attempts remaining..."

# Attempt 2
POST /api/v1/auth/login
{
  "email": "ratelimit@test.com",
  "password": "wrong2"
}
Response: "Invalid credentials. 3 attempts remaining..."

# ... continue until 5th attempt
```

### Step 3: Successful Login Resets Counter
```bash
POST /api/v1/auth/login
{
  "email": "ratelimit@test.com",
  "password": "SecurePass123!"
}
# Expected: 200 OK - Counter reset to 0
```

---

## 🚫 Test 4: Account Lockout

### Step 1: Register User
```bash
POST /api/v1/auth/register
{
  "email": "lockout@test.com",
  "password": "SecurePass123!"
}
```

### Step 2: Make 5 Failed Attempts
```bash
# Attempts 1-4: Shows remaining attempts
# Attempt 5: Account locked!

POST /api/v1/auth/login
{
  "email": "lockout@test.com",
  "password": "wrong5"
}

Response (403 Forbidden):
{
  "detail": "Account locked due to 5 failed login attempts. Try again in 15 minutes."
}
```

### Step 3: Try Correct Password While Locked
```bash
POST /api/v1/auth/login
{
  "email": "lockout@test.com",
  "password": "SecurePass123!"  ← Correct password!
}

Response (403 Forbidden):
{
  "detail": "Account is locked... Try again in 12 minutes."
}
```

### Step 4: Wait 15 Minutes (or change config to 1 minute for testing)
```bash
# In .env:
ACCOUNT_LOCKOUT_MINUTES=1

# Restart backend, wait 1 minute, then:

POST /api/v1/auth/login
{
  "email": "lockout@test.com",
  "password": "SecurePass123!"
}

Response (200 OK):
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
# Account unlocked! Counter reset!
```

---

## 🎯 Quick Test in Swagger UI

### 1. Email Validation
- Go to /auth/register
- Try: `invalid-email` → Should fail
- Try: `valid@test.com` → Should succeed

### 2. Refresh Token
- Login → Copy both tokens
- Use access token in "Authorize" button
- Test protected endpoint (e.g., /chat)
- Go to /auth/refresh → Paste refresh token
- Get new access token

### 3. Rate Limiting
- Create account
- Login with wrong password 4 times
- Watch warning messages count down
- Login with correct password
- Check logs: `failed attempts from X`

### 4. Account Lockout
- Create account
- Login with wrong password 5 times
- Try with correct password → Locked!
- Wait 15 minutes
- Try again → Unlocked!

---

## 📊 Monitor in Real-time

### Watch Logs
```bash
# In another terminal:
tail -f logs/auth_service.log
```

You'll see:
```
INFO: Attempting to authenticate user: test@example.com
WARNING: Authentication failed - invalid password (attempt 1)
WARNING: Authentication failed - invalid password (attempt 2)
ERROR: Account locked for test@example.com (locked until ...)
INFO: Successful login, resetting failed attempts from 2
```

---

## 🧪 Testing Checklist

- [ ] Email validation rejects invalid emails
- [ ] Email validation accepts valid emails
- [ ] Login returns both access and refresh tokens
- [ ] Refresh endpoint returns new access token
- [ ] Invalid refresh token returns 401
- [ ] Failed logins show remaining attempts
- [ ] 5th failed login locks account
- [ ] Locked account returns 403
- [ ] Locked account shows time remaining
- [ ] After 15 minutes, account auto-unlocks
- [ ] Successful login resets failed attempts
- [ ] All events logged in auth_service.log

---

## ⚙️ Configuration for Testing

Create/update `.env`:
```env
# For easier testing, use shorter timeouts
JWT_EXPIRE_MINUTES=5          # Access token expires fast (5 min)
JWT_REFRESH_EXPIRE_DAYS=30    # Refresh token lasts long (30 days)
MAX_LOGIN_ATTEMPTS=3          # Lock after 3 attempts
ACCOUNT_LOCKOUT_MINUTES=1     # Only 1 minute lockout for testing
```

**Remember**: Reset to production values before deployment!

---

## 🆘 Troubleshooting

### Database out of sync?
```bash
rm genai.db
python run.py
# Fresh database with new schema
```

### Need to unlock account manually?
```python
# unlock_account.py
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == "user@example.com").first()
user.locked_until = None
user.failed_login_attempts = 0
db.commit()
print("Account unlocked!")
```

### Check token validity
Use https://jwt.io to decode tokens and check expiration

---

## 📚 Full Documentation

For detailed information, see:
- [SECURITY_FEATURES.md](SECURITY_FEATURES.md) - Complete guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - What was implemented
- [README.md](README.md) - Updated project docs

---

**Happy Testing! 🎉**
