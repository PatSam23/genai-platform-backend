# Security Features Documentation

This document covers the advanced security features implemented in the authentication system.

## Table of Contents
1. [Email Validation](#email-validation)
2. [Refresh Tokens](#refresh-tokens)
3. [Rate Limiting](#rate-limiting)
4. [Account Lockout](#account-lockout)
5. [Configuration](#configuration)
6. [Testing](#testing)

---

## Email Validation

### Overview
Email validation ensures that only properly formatted email addresses can be registered. The system uses the `email-validator` library for RFC-compliant validation.

### Features
- **Format Validation**: Checks for valid email structure (e.g., `user@example.com`)
- **Normalization**: Converts emails to a standardized format
- **Domain Validation**: Validates domain name syntax
- **Error Messages**: Provides specific feedback on validation failures

### Implementation
```python
from app.core.security import validate_email_format

is_valid, result = validate_email_format("user@example.com")
if is_valid:
    normalized_email = result  # Use normalized email
else:
    error_message = result  # Display error to user
```

### API Behavior
When registering with an invalid email:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=invalid-email" \
  -d "password=SecurePass123!"

# Response (400 Bad Request):
{
  "detail": "Invalid email format: The email address is not valid. It must have exactly one @-sign."
}
```

### Examples

#### Valid Emails
✅ `user@example.com`  
✅ `john.doe@company.co.uk`  
✅ `admin+test@domain.com`  
✅ `user_123@sub.domain.com`

#### Invalid Emails
❌ `invalid-email` → "Must have exactly one @-sign"  
❌ `user@` → "Domain name is missing"  
❌ `@example.com` → "Local part is missing"  
❌ `user @example.com` → "Spaces not allowed"

---

## Refresh Tokens

### Overview
Refresh tokens provide a secure way to obtain new access tokens without requiring users to re-enter credentials. Access tokens are short-lived (60 minutes), while refresh tokens last longer (30 days).

### Token Lifecycle
```
1. User logs in → Receives access_token (60min) + refresh_token (30days)
2. Access token expires → Frontend uses refresh_token to get new access_token
3. Continue using new access_token
4. Refresh token expires → User must log in again
```

### Implementation

#### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Refresh Endpoint
```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Security Features
- **Separate Tokens**: Refresh tokens cannot be used for API access
- **Type Checking**: Refresh endpoint validates token type
- **User Validation**: Verifies user exists and is active
- **Logging**: All refresh attempts are logged

### Frontend Integration Example
```javascript
// Store both tokens after login
const { access_token, refresh_token } = await login(email, password);
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// Refresh access token when it expires
async function refreshAccessToken() {
  const refresh_token = localStorage.getItem('refresh_token');
  
  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token })
  });
  
  const { access_token } = await response.json();
  localStorage.setItem('access_token', access_token);
  return access_token;
}

// Auto-retry failed requests with token refresh
async function apiRequest(url, options = {}) {
  let token = localStorage.getItem('access_token');
  
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  
  // If 401, try refreshing token and retry
  if (response.status === 401) {
    token = await refreshAccessToken();
    response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });
  }
  
  return response;
}
```

### Configuration
```python
# .env file
JWT_EXPIRE_MINUTES=60           # Access token validity (1 hour)
JWT_REFRESH_EXPIRE_DAYS=30      # Refresh token validity (30 days)
```

---

## Rate Limiting

### Overview
Rate limiting protects against brute force attacks by tracking failed login attempts. After too many failed attempts, the system provides warnings and eventually locks the account.

### How It Works
1. **First Failed Login**: Counter increments, user gets warning
2. **Subsequent Failures**: Counter increments, remaining attempts shown
3. **Max Attempts Reached**: Account locked for configured duration

### Features
- **Attempt Tracking**: Counts failed login attempts per user
- **Progressive Warnings**: Shows remaining attempts before lockout
- **Automatic Reset**: Counter resets on successful login
- **Timestamp Tracking**: Records last login attempt time

### User Experience

#### Failed Login Attempts
```bash
# 1st failed attempt
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=user@example.com" \
  -d "password=wrong"

# Response (401):
{
  "detail": "Invalid credentials. 4 attempts remaining before account lockout."
}

# 2nd failed attempt
# Response (401):
{
  "detail": "Invalid credentials. 3 attempts remaining before account lockout."
}

# ... continues until 5th attempt triggers lockout
```

#### Successful Login Resets Counter
```bash
# After 2 failed attempts, successful login resets counter
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=user@example.com" \
  -d "password=correct"

# Response (200):
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}

# Counter is reset to 0, lockout cleared
```

### Database Fields
```python
class User(Base):
    failed_login_attempts: int = 0           # Current count of failed attempts
    last_login_attempt: datetime = None      # Timestamp of last attempt
```

### Configuration
```python
# .env file
MAX_LOGIN_ATTEMPTS=5  # Number of failed attempts before lockout
```

### Logging
All login attempts are logged:
```
INFO:auth_service:Attempting to authenticate user: user@example.com
WARNING:auth_service:Authentication failed - invalid password for: user@example.com (attempt 1)
INFO:auth_service:Successful login for user@example.com, resetting failed attempts from 2
```

---

## Account Lockout

### Overview
After reaching the maximum failed login attempts, accounts are temporarily locked to prevent brute force attacks. Users must wait for the lockout period to expire before attempting to log in again.

### Lockout Behavior

#### Triggering Lockout
```bash
# 5th failed login attempt
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=user@example.com" \
  -d "password=wrong"

# Response (403 Forbidden):
{
  "detail": "Account locked due to 5 failed login attempts. Try again in 15 minutes."
}
```

#### Lockout Period Active
```bash
# Attempt to login while locked (after 5 minutes)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=user@example.com" \
  -d "password=correct"

# Response (403 Forbidden):
{
  "detail": "Account is locked due to too many failed login attempts. Try again in 10 minutes."
}
```

#### Lockout Expiration
```bash
# After 15 minutes, lockout expires automatically
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=user@example.com" \
  -d "password=correct"

# Response (200):
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}

# Account is unlocked, counters reset
```

### Features
- **Time-Based**: Lockout duration configurable (default 15 minutes)
- **Automatic Expiry**: No manual intervention needed
- **Immediate Reset**: Successful login after expiry resets all counters
- **Dynamic Messages**: Shows exact time remaining during lockout
- **Comprehensive Logging**: All lockout events logged for security audit

### Database Fields
```python
class User(Base):
    locked_until: datetime = None  # Timestamp when lockout expires
```

### Implementation Flow
```python
1. Check if locked_until > now
   YES → Return 403 with time remaining
   NO → Continue to password verification

2. Verify password
   FAIL → Increment failed_login_attempts
          If attempts >= MAX → Set locked_until = now + LOCKOUT_MINUTES
   SUCCESS → Reset failed_login_attempts = 0
             Reset locked_until = None
```

### Configuration
```python
# .env file
ACCOUNT_LOCKOUT_MINUTES=15  # Duration of account lockout
MAX_LOGIN_ATTEMPTS=5        # Attempts before lockout
```

### Security Considerations
- **Prevents Brute Force**: Significantly slows down password guessing attacks
- **User-Specific**: Each user tracked independently
- **No Permanent Lock**: Automatic expiration prevents false positives
- **Clear Communication**: Users know exactly when they can retry

### Monitoring
Check logs for lockout events:
```bash
# View lockout events
grep "Account locked" logs/auth_service.log

# Example output:
ERROR:auth_service:Account locked for user@example.com due to 5 failed attempts (locked until 2024-01-15 14:30:00)
```

---

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=sqlite:///./genai.db

# JWT Settings
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
JWT_REFRESH_EXPIRE_DAYS=30

# Security Settings
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=15

# LLM Provider
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

### Settings Class
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 30
    
    # Security settings
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15
```

### Production Recommendations

#### Strong Secret Key
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use in .env
JWT_SECRET_KEY=XOyqz9kL7mN8pQ2rS5tU6vW7xY8zA1bC2dE3fG4hI5j
```

#### Adjusted Timeouts
```bash
# Production values
JWT_EXPIRE_MINUTES=15              # Shorter access token
JWT_REFRESH_EXPIRE_DAYS=7          # Shorter refresh token
MAX_LOGIN_ATTEMPTS=3               # Stricter rate limiting
ACCOUNT_LOCKOUT_MINUTES=30         # Longer lockout
```

---

## Testing

### Setup Test Environment

#### 1. Install Dependencies
```bash
cd genai-platform-backend
pip install -r requirements.txt
```

#### 2. Create .env File
```bash
echo "DATABASE_URL=sqlite:///./test.db" > .env
echo "JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
```

#### 3. Initialize Database
```bash
# The database will be created automatically on first run
python run.py
```

### Testing Email Validation

#### Test 1: Valid Email
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=john.doe@example.com" \
  -d "password=SecurePass123!"

# Expected: 200 OK
```

#### Test 2: Invalid Email Format
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=invalid-email" \
  -d "password=SecurePass123!"

# Expected: 400 Bad Request with email validation error
```

#### Test 3: Email Normalization
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=JOHN.DOE@EXAMPLE.COM" \
  -d "password=SecurePass123!"

# Email will be normalized to lowercase
```

### Testing Refresh Tokens

#### Test 1: Login and Get Tokens
```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=refresh@test.com" \
  -d "password=SecurePass123!"

# Login
LOGIN_RESPONSE=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=refresh@test.com" \
  -d "password=SecurePass123!")

echo $LOGIN_RESPONSE
# Should contain both access_token and refresh_token
```

#### Test 2: Use Refresh Token
```bash
# Extract refresh token from login response
REFRESH_TOKEN="<paste_refresh_token_here>"

# Get new access token
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"

# Expected: New access_token
```

#### Test 3: Invalid Refresh Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "invalid.token.here"}'

# Expected: 401 Unauthorized
```

### Testing Rate Limiting

#### Test 1: Multiple Failed Attempts
```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=ratelimit@test.com" \
  -d "password=SecurePass123!"

# Attempt 1 (wrong password)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=ratelimit@test.com" \
  -d "password=wrong1"
# Response: "4 attempts remaining"

# Attempt 2
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=ratelimit@test.com" \
  -d "password=wrong2"
# Response: "3 attempts remaining"

# Attempt 3
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=ratelimit@test.com" \
  -d "password=wrong3"
# Response: "2 attempts remaining"
```

#### Test 2: Reset on Successful Login
```bash
# After 2 failed attempts
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=ratelimit@test.com" \
  -d "password=SecurePass123!"

# Expected: 200 OK with tokens, counter reset
```

### Testing Account Lockout

#### Test 1: Trigger Lockout
```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=lockout@test.com" \
  -d "password=SecurePass123!"

# Make 5 failed attempts
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v1/auth/login" \
    -d "email=lockout@test.com" \
    -d "password=wrong$i"
  echo ""
done

# Last response should be: "Account locked due to 5 failed login attempts"
```

#### Test 2: Locked Account Behavior
```bash
# Try to login with correct password while locked
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=lockout@test.com" \
  -d "password=SecurePass123!"

# Expected: 403 Forbidden
# "Account is locked... Try again in X minutes."
```

#### Test 3: Lockout Expiration
```bash
# Wait 15 minutes (or change ACCOUNT_LOCKOUT_MINUTES=1 for testing)
# Then try again
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=lockout@test.com" \
  -d "password=SecurePass123!"

# Expected: 200 OK with tokens
```

### Testing with Swagger UI

Navigate to `http://localhost:8000/docs`

#### 1. Register User
- Click on `POST /api/v1/auth/register`
- Click "Try it out"
- Enter email and password
- Click "Execute"

#### 2. Login
- Click on `POST /api/v1/auth/login`
- Enter credentials
- Copy both `access_token` and `refresh_token`

#### 3. Test Protected Endpoint
- Click "Authorize" button (top right)
- Paste access_token
- Try a protected endpoint like `/api/v1/chat`

#### 4. Refresh Token
- Click on `POST /api/v1/auth/refresh`
- Paste refresh_token in request body
- Get new access_token

### Automated Testing Script

Create `test_security.py`:

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_email_validation():
    """Test email validation"""
    print("\n=== Testing Email Validation ===")
    
    # Valid email
    response = requests.post(f"{BASE_URL}/auth/register", data={
        "email": "valid@example.com",
        "password": "SecurePass123!"
    })
    print(f"Valid email: {response.status_code}")
    
    # Invalid email
    response = requests.post(f"{BASE_URL}/auth/register", data={
        "email": "invalid-email",
        "password": "SecurePass123!"
    })
    print(f"Invalid email: {response.status_code} - {response.json()['detail']}")

def test_refresh_tokens():
    """Test refresh token flow"""
    print("\n=== Testing Refresh Tokens ===")
    
    # Register
    email = f"refresh_{int(time.time())}@test.com"
    requests.post(f"{BASE_URL}/auth/register", data={
        "email": email,
        "password": "SecurePass123!"
    })
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "email": email,
        "password": "SecurePass123!"
    })
    tokens = response.json()
    print(f"Login successful: access_token={tokens['access_token'][:20]}...")
    print(f"Refresh token: {tokens['refresh_token'][:20]}...")
    
    # Refresh
    response = requests.post(f"{BASE_URL}/auth/refresh", json={
        "refresh_token": tokens['refresh_token']
    })
    new_token = response.json()
    print(f"Refreshed: new_access_token={new_token['access_token'][:20]}...")

def test_rate_limiting():
    """Test rate limiting and account lockout"""
    print("\n=== Testing Rate Limiting ===")
    
    # Register
    email = f"ratelimit_{int(time.time())}@test.com"
    requests.post(f"{BASE_URL}/auth/register", data={
        "email": email,
        "password": "SecurePass123!"
    })
    
    # Failed attempts
    for i in range(6):
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "email": email,
            "password": f"wrong{i}"
        })
        print(f"Attempt {i+1}: {response.status_code} - {response.json()['detail']}")
        
        if response.status_code == 403:
            print("Account locked!")
            break

if __name__ == "__main__":
    test_email_validation()
    test_refresh_tokens()
    test_rate_limiting()
```

Run the script:
```bash
python test_security.py
```

### Monitoring

Check logs for security events:

```bash
# View authentication logs
tail -f logs/auth_service.log

# Search for lockout events
grep "Account locked" logs/auth_service.log

# Search for failed attempts
grep "Authentication failed" logs/auth_service.log

# Search for successful logins
grep "authenticated successfully" logs/auth_service.log
```

---

## Database Migration

Since new fields were added to the User model, you need to update your database:

### Option 1: Fresh Start (Development Only)
```bash
# Delete old database
rm genai.db

# Restart backend - database will be recreated with new schema
python run.py
```

### Option 2: Manual Migration (Preserve Data)
```python
# migration.py
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

# Add new columns
with engine.connect() as conn:
    conn.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0")
    conn.execute("ALTER TABLE users ADD COLUMN locked_until DATETIME")
    conn.execute("ALTER TABLE users ADD COLUMN last_login_attempt DATETIME")
    conn.commit()

print("Migration completed!")
```

Run migration:
```bash
python migration.py
```

---

## Security Best Practices

### 1. Environment Variables
- **Never** commit `.env` to version control
- Use strong, random `JWT_SECRET_KEY`
- Rotate secrets periodically

### 2. Token Security
- Store refresh tokens securely (httpOnly cookies recommended)
- Never log token values
- Implement token revocation for logout

### 3. Rate Limiting
- Monitor failed login attempts
- Adjust `MAX_LOGIN_ATTEMPTS` based on threat level
- Consider IP-based rate limiting for additional protection

### 4. Account Lockout
- Provide account recovery mechanism (email reset)
- Log all lockout events for security audit
- Consider progressive delays instead of hard lockout

### 5. Email Validation
- Validate on both frontend and backend
- Consider email verification (send confirmation link)
- Implement email change verification

---

## Troubleshooting

### Issue: "Invalid email format" for valid emails
**Solution**: Update `email-validator` package
```bash
pip install --upgrade email-validator
```

### Issue: Refresh token returns 401
**Possible Causes**:
- Token expired (30 days default)
- User account deactivated
- Invalid JWT signature

**Solution**: Check token expiration and user status

### Issue: Account locked permanently
**Cause**: `locked_until` not being reset

**Solution**: Run manual unlock
```python
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == "user@example.com").first()
user.locked_until = None
user.failed_login_attempts = 0
db.commit()
```

### Issue: Database migration failed
**Solution**: Use fresh database for development
```bash
rm genai.db
python run.py
```

---

## Summary

The authentication system now includes:

✅ **Email Validation**: RFC-compliant email format checking  
✅ **Refresh Tokens**: Long-lived tokens for seamless re-authentication  
✅ **Rate Limiting**: Failed attempt tracking with progressive warnings  
✅ **Account Lockout**: Automatic 15-minute lockout after 5 failed attempts  
✅ **Comprehensive Logging**: All security events logged for audit  
✅ **Configurable**: All thresholds configurable via environment variables

These features significantly enhance security while maintaining a good user experience.
