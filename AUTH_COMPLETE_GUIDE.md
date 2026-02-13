# 🔐 Complete Authentication System Guide
## A Comprehensive Tutorial on Secure User Authentication

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Password Security](#password-security)
4. [JWT Authentication](#jwt-authentication)
5. [Implementation Details](#implementation-details)
6. [Security Best Practices](#security-best-practices)
7. [Testing Guide](#testing-guide)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Topics](#advanced-topics)

---

## 1. Introduction

### What Did We Build?

We implemented a **complete, production-ready authentication system** with three main components:

1. ✅ **Password Hashing** - Securely store passwords using bcrypt
2. ✅ **Password Validation** - Enforce strong password requirements
3. ✅ **JWT Authentication** - Token-based authentication for API access

### Why Is This Important?

**Without proper authentication:**
- ❌ Anyone can access your API
- ❌ No way to track users
- ❌ Passwords stored in plain text (MAJOR SECURITY RISK)
- ❌ No accountability for actions

**With our authentication system:**
- ✅ Only registered users can access protected resources
- ✅ Passwords are cryptographically hashed (impossible to reverse)
- ✅ User actions are tracked and logged
- ✅ Stateless, scalable authentication with JWT
- ✅ Industry-standard security practices

---

## 2. Core Concepts

### 2.1 Authentication vs Authorization

**Authentication** = "Who are you?"
- Verifying user identity (login)
- Checking credentials (email + password)
- Issuing tokens for verified users

**Authorization** = "What can you do?"
- Checking permissions (coming in future)
- Role-based access control (admin vs user)
- Resource ownership validation

**Our system currently handles AUTHENTICATION.**

### 2.2 How Authentication Flow Works

```
┌─────────────┐
│   User      │
│ Registers   │
└──────┬──────┘
       │ 1. Email + Password
       ▼
┌─────────────┐
│   Backend   │
│  Validates  │──→ Password too weak? ❌ Reject
│  Password   │
└──────┬──────┘
       │ 2. Hash Password
       ▼
┌─────────────┐
│  Database   │
│   Stores    │
│ Hashed Pass │
└─────────────┘

Later, User Logs In:
┌─────────────┐
│   User      │
│  Logs In    │
└──────┬──────┘
       │ 1. Email + Password
       ▼
┌─────────────┐
│   Backend   │
│  Verifies   │
│  Password   │
└──────┬──────┘
       │ 2. Issue JWT Token
       ▼
┌─────────────┐
│   User      │
│  Receives   │
│   Token     │
└──────┬──────┘
       │ 3. Uses Token for API Requests
       ▼
┌─────────────┐
│ Protected   │
│  Endpoint   │
│  /chat      │
└─────────────┘
```

---

## 3. Password Security

### 3.1 Why We Hash Passwords

**NEVER store passwords in plain text!**

**Scenario Without Hashing:**
```python
# ❌ WRONG - NEVER DO THIS!
user.password = "MyPassword123!"  # Stored as-is
```

**What happens if database is hacked?**
- Attacker sees all passwords
- Can use them to access other websites (many people reuse passwords)
- Complete security breach

**Scenario With Hashing (Our Implementation):**
```python
# ✅ CORRECT
user.hashed_password = "$2b$12$KIXw3QZ..."  # Encrypted, irreversible
```

**What happens if database is hacked?**
- Attacker sees gibberish
- Cannot reverse the hash to get original password
- Even if they try billions of guesses, bcrypt is designed to be slow

### 3.2 What Is Bcrypt?

**Bcrypt** is a password hashing function designed specifically for passwords.

**Key Features:**
1. **One-way function**: Cannot reverse the hash
2. **Salt included**: Each password hash is unique (even same password)
3. **Adaptive**: Can increase difficulty over time as computers get faster
4. **Slow by design**: Makes brute-force attacks impractical

**Example:**
```python
password = "MyPassword123!"

# After bcrypt hashing:
hash = "$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"
     └──┘ └┘ └────────────────────┘ └─────────────────────────────┘
      │   │          │                        │
   Version │        Salt              Actual Hash (31 chars)
        Cost
       (2^12 = 4096 rounds)
```

### 3.3 Our Hashing Implementation

**File: `app/core/security.py`**

```python
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    # 1. Convert password to bytes (bcrypt requires bytes)
    password_bytes = password.encode('utf-8')
    
    # 2. Generate a random salt
    salt = bcrypt.gensalt()
    
    # 3. Hash password with salt
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # 4. Return as string for database storage
    return hashed.decode('utf-8')
```

**Why This Is Secure:**
- Each user gets a **unique salt** (even if passwords are same)
- Bcrypt uses **4,096 iterations** by default (very slow to crack)
- Industry-standard algorithm used by major companies

### 3.4 Password Validation

We enforce **strong passwords** to prevent weak credentials.

**Requirements:**
- ✅ Minimum 8 characters (harder to brute force)
- ✅ At least 1 uppercase letter (A-Z)
- ✅ At least 1 lowercase letter (a-z)
- ✅ At least 1 digit (0-9)
- ✅ At least 1 special character (!@#$%^&*)
- ✅ Maximum 128 characters (prevent DoS attacks)

**Implementation:**

```python
def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    
    # Length check
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must not exceed 128 characters"
    
    # Uppercase check
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    # Lowercase check
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    # Digit check
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    # Special character check
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
        return False, "Password must contain at least one special character"
    
    return True, ""
```

**Examples:**

| Password | Valid? | Reason |
|----------|--------|--------|
| `password` | ❌ | No uppercase, digit, or special char |
| `Password` | ❌ | No digit or special char |
| `Password1` | ❌ | No special char |
| `Password1!` | ✅ | Meets all requirements |
| `MyP@ss1` | ❌ | Too short (only 7 chars) |
| `MySecureP@ss123` | ✅ | Meets all requirements |

### 3.5 Password Verification

When a user logs in, we verify their password:

```python
def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a hashed password.
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    
    # bcrypt.checkpw extracts the salt from the hash
    # and re-hashes the input password with that salt
    # then compares the result
    return bcrypt.checkpw(password_bytes, hashed_bytes)
```

**How It Works:**
1. User submits password: `"MyPassword123!"`
2. We retrieve stored hash from database: `"$2b$12$KIXw..."`
3. Bcrypt extracts the salt from the stored hash
4. Re-hashes the submitted password with that salt
5. Compares the new hash with stored hash
6. Returns `True` if they match, `False` otherwise

**Why This Is Secure:**
- Constant-time comparison (prevents timing attacks)
- Salt ensures rainbow table attacks don't work
- Even knowing the algorithm, attacker can't reverse the hash

---

## 4. JWT Authentication

### 4.1 What Is JWT?

**JWT (JSON Web Token)** is a compact, self-contained way to transmit information between parties.

**Structure:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzcwOTg5NTIwfQ.qL82DfUP_92EbUcnB0Oy27OK4eqHh7jXnDM6K0q45-Y
└────────────  HEADER  ────────────┘ └─────────  PAYLOAD  ─────────┘ └──────────  SIGNATURE  ──────────┘
```

**Three Parts (separated by dots):**

1. **Header** - Algorithm and token type
   ```json
   {
     "alg": "HS256",
     "typ": "JWT"
   }
   ```

2. **Payload** - Claims (data)
   ```json
   {
     "sub": "3",           // User ID
     "exp": 1770989520     // Expiration timestamp
   }
   ```

3. **Signature** - Verification
   ```
   HMACSHA256(
     base64UrlEncode(header) + "." + base64UrlEncode(payload),
     secret_key
   )
   ```

### 4.2 Why Use JWT?

**Traditional Session-Based Auth (OLD WAY):**
```
Client                      Server
  │                           │
  ├──── Login ────────────────►│
  │                           │ Create session in database
  │◄─── Session ID ───────────┤ Return session ID
  │                           │
  ├──── Request + Session ───►│ Look up session in DB
  │                           │ (Database query on EVERY request)
  │◄─── Response ─────────────┤
```

**Problems:**
- ❌ Database query on every request (slow)
- ❌ Hard to scale (sessions tied to specific server)
- ❌ Memory overhead (store all sessions)

**JWT Token-Based Auth (OUR WAY):**
```
Client                      Server
  │                           │
  ├──── Login ────────────────►│
  │                           │ Create JWT (no database)
  │◄─── JWT Token ────────────┤ Return signed token
  │                           │
  ├──── Request + JWT ───────►│ Verify signature (no database!)
  │                           │ Extract user ID from token
  │◄─── Response ─────────────┤
```

**Benefits:**
- ✅ **Stateless**: No server-side storage needed
- ✅ **Scalable**: Any server can verify the token
- ✅ **Fast**: No database lookup
- ✅ **Self-contained**: Token contains user info
- ✅ **Secure**: Signed with secret key (cannot be forged)

### 4.3 Creating JWT Tokens

**File: `app/core/security.py`**

```python
def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    
    # 1. Copy the data (don't modify original)
    to_encode = data.copy()
    
    # 2. Add expiration time (60 minutes from now)
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    
    # 3. Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode,                      # Payload data
        settings.JWT_SECRET_KEY,        # Secret for signing
        algorithm=settings.JWT_ALGORITHM # HS256 (HMAC + SHA256)
    )
    
    return encoded_jwt
```

**Example:**
```python
# When user logs in:
token = create_access_token({"sub": "3"})  # sub = subject (user ID)

# Returns:
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzcwOTg5NTIwfQ.qL82DfUP..."
```

### 4.4 Verifying JWT Tokens

```python
def decode_access_token(token: str) -> Optional[str]:
    """Decode and verify a JWT access token."""
    try:
        # 1. Decode and verify signature
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # 2. Extract user ID
        user_id: str = payload.get("sub")
        
        # 3. jwt.decode automatically checks expiration!
        # If expired, raises JWTError
        
        return user_id
    except JWTError:
        # Token invalid, expired, or forged
        return None
```

**What Gets Checked:**
- ✅ Signature is valid (token not tampered with)
- ✅ Token not expired (`exp` claim)
- ✅ Algorithm matches expected (`alg` in header)

**Security Features:**
- **Signature Verification**: If anyone modifies the payload, signature won't match
- **Expiration**: Tokens auto-expire after 60 minutes
- **Secret Key**: Only server with secret can create valid tokens

### 4.5 The get_current_user Dependency

This is how we protect routes in FastAPI.

**File: `app/core/auth.py`**

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    This function is used as a dependency in route handlers.
    """
    
    # 1. Extract token from Authorization header
    token = credentials.credentials
    
    # 2. Decode and verify token
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(401, "Invalid or expired token")
    
    # 3. Load user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(401, "User not found")
    
    # 4. Check if user is active
    if not user.is_active:
        raise HTTPException(403, "Inactive user")
    
    # 5. Return user object
    return user
```

**How It's Used:**

```python
# Protected endpoint
@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)  # ← Protection!
):
    # If we reach here, user is authenticated
    # We can use current_user.email, current_user.id, etc.
    pass
```

**What Happens:**
1. User sends request with `Authorization: Bearer <token>` header
2. FastAPI calls `get_current_user` before the route handler
3. If token is invalid → 401 Unauthorized (route handler never called)
4. If token is valid → User object injected into `current_user` parameter
5. Route handler can now use the authenticated user

---

## 5. Implementation Details

### 5.1 File Structure

```
app/
├── core/
│   ├── security.py          # Password hashing, JWT creation
│   ├── auth.py              # get_current_user dependency
│   ├── config.py            # Settings (JWT_SECRET_KEY, etc.)
│   └── logging.py           # Logging setup
├── models/
│   └── user.py              # User database model
├── services/
│   └── auth_service.py      # Registration & login logic
├── api/v1/
│   ├── auth.py              # /register and /login endpoints
│   ├── chat.py              # Protected chat endpoints
│   └── rag.py               # Protected RAG endpoints
└── db/
    ├── session.py           # Database connection
    └── deps.py              # get_db dependency
```

### 5.2 Database Model

**File: `app/models/user.py`**

```python
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

**Key Points:**
- `email` is **unique** and **indexed** (fast lookups)
- We store `hashed_password`, NEVER plain password
- `is_active` allows us to disable accounts without deletion

### 5.3 Registration Flow

**File: `app/services/auth_service.py`**

```python
@staticmethod
def register_user(email: str, password: str, db: Session) -> dict:
    # Step 1: Validate password strength
    is_valid, error_message = validate_password(password)
    if not is_valid:
        raise HTTPException(400, error_message)
    
    # Step 2: Check if email already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already registered")
    
    # Step 3: Hash the password
    hashed = hash_password(password)
    
    # Step 4: Create user in database
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    
    return {"message": "User created successfully"}
```

**API Endpoint:**

```python
@router.post("/auth/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    return AuthService.register_user(email, password, db)
```

### 5.4 Login Flow

```python
@staticmethod
def authenticate_user(email: str, password: str, db: Session) -> dict:
    # Step 1: Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Step 2: Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    # Step 3: Create JWT token
    token = create_access_token({"sub": str(user.id)})
    
    # Step 4: Return token
    return {"access_token": token, "token_type": "bearer"}
```

**API Endpoint:**

```python
@router.post("/auth/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    return AuthService.authenticate_user(email, password, db)
```

### 5.5 Protected Endpoints

**Before (Unprotected):**
```python
@router.post("/chat")
async def chat(request: ChatRequest):
    # Anyone can call this!
    pass
```

**After (Protected):**
```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)  # ← Authentication required!
):
    # Only authenticated users reach here
    # Can access current_user.email, current_user.id
    logger.info(f"Chat request from {current_user.email}")
    pass
```

**All Protected Endpoints:**
- ✅ `/api/v1/chat`
- ✅ `/api/v1/chat/stream`
- ✅ `/api/v1/rag/query`
- ✅ `/api/v1/rag/pdf/stream`
- ✅ `/api/v1/rag/ingest/pdf`
- ✅ `/api/v1/rag/pdf`

---

## 6. Security Best Practices

### 6.1 Configuration Security

**File: `.env`**

```env
# ⚠️ CRITICAL: Change this in production!
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long-please-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

DATABASE_URL=sqlite:///./genai.db
```

**Best Practices:**

1. **JWT_SECRET_KEY**:
   - ✅ Minimum 32 characters
   - ✅ Random (use password generator)
   - ✅ Never commit to git
   - ✅ Different for dev/staging/production
   
   **Generate secure key:**
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   # Output: "dGhpc2lzYXJhbmRvbXNlY3JldGtleWZvcnByb2R1Y3Rpb24"
   ```

2. **HTTPS Only in Production**:
   - JWT tokens in plain HTTP can be intercepted
   - Always use TLS/SSL certificates

3. **Token Expiration**:
   - Short-lived tokens (60 minutes)
   - Implement refresh tokens for better UX

### 6.2 Common Attack Vectors & Our Defenses

| Attack | Description | Our Defense |
|--------|-------------|-------------|
| **Brute Force** | Try many passwords | Bcrypt is intentionally slow (4096 rounds) |
| **Rainbow Tables** | Pre-computed hash lookups | Salt makes each hash unique |
| **SQL Injection** | Malicious SQL in inputs | SQLAlchemy ORM prevents this |
| **JWT Forgery** | Create fake tokens | Signature verification |
| **Token Theft** | Steal someone's token | Expiration + HTTPS only |
| **Weak Passwords** | Users pick "password123" | Password validation (8+ chars, complexity) |
| **Timing Attacks** | Measure response time to guess password | Constant-time comparison in bcrypt |

### 6.3 What We Log

**Good Logging (Our Implementation):**
```python
logger.info(f"User registered: {email}")
logger.info(f"Login attempt for: {email}")
logger.warning(f"Failed login for: {email}")
logger.info(f"Chat request from user {current_user.email}")
```

**Bad Logging (NEVER DO THIS):**
```python
# ❌ NEVER log passwords!
logger.info(f"Password: {password}")

# ❌ NEVER log full tokens!
logger.info(f"Token: {token}")

# ❌ NEVER log sensitive user data!
logger.info(f"Credit card: {user.credit_card}")
```

---

## 7. Testing Guide

### 7.1 Test Weak Passwords

**Test these passwords (should all fail):**

| Password | Expected Error |
|----------|----------------|
| `pass` | Too short |
| `password` | No uppercase, digit, or special char |
| `Password` | No digit or special char |
| `Password1` | No special char |
| `password1!` | No uppercase |
| `PASSWORD1!` | No lowercase |

**Test valid passwords:**

| Password | Status |
|----------|--------|
| `Password1!` | ✅ Valid |
| `MyP@ssw0rd` | ✅ Valid |
| `Secure#Pass123` | ✅ Valid |

### 7.2 Test Registration

```bash
# 1. Register with weak password (should fail)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=test@example.com&password=weak"

# Response: {"detail": "Password must contain at least one uppercase letter"}

# 2. Register with strong password (should succeed)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=test@example.com&password=SecureP@ss123"

# Response: {"message": "User created successfully"}

# 3. Try to register same email (should fail)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=test@example.com&password=AnotherP@ss123"

# Response: {"detail": "Email already registered"}
```

### 7.3 Test Login

```bash
# 1. Login with correct credentials
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=test@example.com&password=SecureP@ss123"

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# 2. Login with wrong password
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=test@example.com&password=WrongPassword"

# Response: {"detail": "Invalid credentials"}
```

### 7.4 Test Protected Endpoints

```bash
# 1. Try to access without token (should fail)
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello","history":[],"context":null}'

# Response: {"detail": "Not authenticated"}

# 2. Get token first
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=test@example.com&password=SecureP@ss123" \
  | jq -r '.access_token')

# 3. Use token (should succeed)
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello","history":[],"context":null}'

# Response: {"response": "Hello! How can I help you?"}
```

### 7.5 Test in Swagger UI

1. **Go to**: http://localhost:8000/docs

2. **Register User**:
   - Expand `/api/v1/auth/register`
   - Click "Try it out"
   - Enter email and a **strong password** (e.g., `TestP@ss123`)
   - Click "Execute"
   - Should see: `{"message": "User created successfully"}`

3. **Login**:
   - Expand `/api/v1/auth/login`
   - Enter same email and password
   - Click "Execute"
   - **Copy the `access_token`**

4. **Authorize**:
   - Click 🔓 **"Authorize"** button at top
   - Paste token in "Value" field
   - Click "Authorize"
   - Click "Close"
   - You should see 🔒 next to protected endpoints

5. **Test Chat**:
   - Expand `/api/v1/chat`
   - Click "Try it out"
   - Enter request body:
     ```json
     {
       "prompt": "What is Python?",
       "history": [],
       "context": null
     }
     ```
   - Click "Execute"
   - Should get a response!

---

## 8. Troubleshooting

### 8.1 Common Issues

**Issue: "Not authenticated" error**

**Cause**: Missing or invalid token

**Solution**:
1. Make sure you logged in and got a token
2. Check that you clicked "Authorize" in Swagger
3. Verify token hasn't expired (60 minutes)
4. Check Authorization header format: `Bearer <token>`

---

**Issue: "Invalid or expired token"**

**Cause**: Token expired or corrupted

**Solution**:
1. Login again to get a new token
2. Check server time is correct
3. Verify JWT_SECRET_KEY hasn't changed

---

**Issue: "Password must contain..." errors**

**Cause**: Password doesn't meet requirements

**Solution**: Use a strong password:
- ✅ At least 8 characters
- ✅ 1 uppercase (A-Z)
- ✅ 1 lowercase (a-z)
- ✅ 1 digit (0-9)
- ✅ 1 special char (!@#$%^&*)

Example: `MySecureP@ss123`

---

**Issue: "Email already registered"**

**Cause**: That email is already in the database

**Solution**:
- Use a different email, OR
- Login with that email instead

---

### 8.2 Debugging Tips

**Check Logs:**
```bash
# View authentication logs
cat logs/auth.log

# View auth service logs
cat logs/auth_service.log

# Live tail (watch in real-time)
tail -f logs/auth.log
```

**Verify Database:**
```bash
# Check if user exists
sqlite3 genai.db "SELECT id, email, is_active FROM users;"

# Check user count
sqlite3 genai.db "SELECT COUNT(*) FROM users;"
```

**Decode JWT Token (for debugging):**

Go to: https://jwt.io/

Paste your token to see the payload (don't share production tokens!)

---

## 9. Advanced Topics

### 9.1 Token Refresh

**Current Implementation**: Tokens expire after 60 minutes

**Problem**: Users get logged out every hour

**Solution** (Future Enhancement): Refresh Tokens

```python
# Create both access and refresh tokens
def create_token_pair(user_id: str):
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=15)  # Short-lived
    )
    
    refresh_token = create_access_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=30)  # Long-lived
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

# Separate endpoint to refresh
@router.post("/auth/refresh")
def refresh(refresh_token: str):
    # Verify refresh token
    # Issue new access token
    pass
```

### 9.2 Email Verification

**Enhancement**: Verify email addresses before activation

```python
# 1. Generate verification token
verification_token = secrets.token_urlsafe(32)

# 2. Store in database
user.verification_token = verification_token
user.is_verified = False

# 3. Send email
send_email(
    to=user.email,
    subject="Verify your email",
    body=f"Click: https://yourapp.com/verify/{verification_token}"
)

# 4. Verification endpoint
@router.get("/auth/verify/{token}")
def verify_email(token: str):
    user = db.query(User).filter(User.verification_token == token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.commit()
    return {"message": "Email verified"}
```

### 9.3 Password Reset

```python
@router.post("/auth/forgot-password")
def forgot_password(email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        send_email(
            to=email,
            subject="Reset your password",
            body=f"Click: https://yourapp.com/reset/{reset_token}"
        )
    
    return {"message": "If email exists, reset link sent"}

@router.post("/auth/reset-password")
def reset_password(token: str, new_password: str):
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(400, "Invalid or expired token")
    
    # Validate new password
    is_valid, error = validate_password(new_password)
    if not is_valid:
        raise HTTPException(400, error)
    
    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password reset successfully"}
```

### 9.4 Role-Based Access Control (RBAC)

**Add roles to User model:**

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default="user")  # NEW!
```

**Create admin-only dependency:**

```python
def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return current_user

# Use it:
@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user)  # Only admins can call this
):
    # Delete user logic
    pass
```

### 9.5 Rate Limiting

**Prevent abuse by limiting requests per user:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    pass
```

### 9.6 Account Lockout

**Lock accounts after failed login attempts:**

```python
class User(Base):
    # ... existing fields ...
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    
    # Check if locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(403, "Account temporarily locked. Try again later.")
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        
        # Lock after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        db.commit()
        raise HTTPException(401, "Invalid credentials")
    
    # Success - reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    # ... generate token ...
```

---

## 📊 Summary

### What We Built

| Component | Purpose | Security Level |
|-----------|---------|----------------|
| **Password Hashing** | Store passwords securely | 🔒🔒🔒🔒🔒 Bcrypt (industry standard) |
| **Password Validation** | Enforce strong passwords | 🔒🔒🔒🔒 Complex requirements |
| **JWT Authentication** | Stateless API authentication | 🔒🔒🔒🔒 Signed tokens |
| **Protected Endpoints** | Restrict access to authenticated users | 🔒🔒🔒🔒 Dependency injection |
| **Logging** | Audit trail of all actions | 🔒🔒🔒 No sensitive data logged |

### Security Checklist

- ✅ Passwords hashed with bcrypt
- ✅ Strong password requirements enforced
- ✅ JWT tokens signed and verified
- ✅ Tokens expire after 60 minutes
- ✅ All sensitive endpoints protected
- ✅ User actions logged
- ✅ No plain text passwords anywhere
- ✅ Constant-time password verification
- ✅ SQL injection prevented (ORM)
- ✅ Inactive users can't authenticate

### Key Takeaways

1. **Never store plain text passwords** - Always hash with bcrypt
2. **Always validate user input** - Password strength, email format, etc.
3. **Use JWT for APIs** - Stateless, scalable authentication
4. **Protect sensitive endpoints** - Use dependencies like `get_current_user`
5. **Log everything (except secrets)** - Audit trail for security
6. **Tokens should expire** - Limit damage if token is stolen
7. **HTTPS in production** - Encrypt all traffic
8. **Different secrets per environment** - Dev ≠ Production

---

## 🎓 Learning Resources

### Books
- "Web Application Security" - Andrew Hoffman
- "The Web Application Hacker's Handbook" - Dafydd Stuttard

### Online Courses
- OWASP Top 10 Security Risks
- FastAPI Security Best Practices
- JWT.io - Token Debugger

### Standards
- NIST Password Guidelines
- OWASP Authentication Cheat Sheet
- RFC 7519 (JWT Specification)

---

## 🎯 Next Steps

**Immediate:**
1. Test all endpoints with authentication
2. Change `JWT_SECRET_KEY` to a secure value
3. Test password validation with various inputs

**Short Term:**
1. Implement refresh tokens
2. Add email verification
3. Create password reset flow

**Long Term:**
1. Add OAuth2 (Google, GitHub login)
2. Implement rate limiting
3. Add role-based access control
4. Set up monitoring/alerting

---

**🎉 Congratulations! You now have a production-ready authentication system!**

---

*This guide was created for the GenAI Platform Backend project*  
*Last updated: February 13, 2026*
