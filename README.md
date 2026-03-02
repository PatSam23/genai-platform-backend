# GenAI Platform Backend

A production-ready backend for generative AI services featuring chat, retrieval-augmented generation (RAG), multi-provider model integrations, and comprehensive security.

## ✨ Features 
 
### Core Functionality
- 💬 **Chat API** - Streaming and non-streaming chat completions
- 📚 **RAG Pipeline** - Document ingestion, vectorization, and retrieval
- 🔌 **Multi-Provider Support** - OpenAI, Hugging Face, Ollama, AWS Bedrock
- 🎯 **Vector Store** - ChromaDB and in-memory options for embeddings

### Security & Authentication
- 🔐 **JWT Authentication** - Stateless, scalable token-based auth
- � **Refresh Tokens** - Long-lived tokens (30 days) for seamless re-authentication
- 🔒 **Password Security** - Bcrypt hashing with strong validation
- ✉️ **Email Validation** - RFC-compliant email format checking
- ⏱️ **Rate Limiting** - Failed login attempt tracking with warnings
- 🚫 **Account Lockout** - Automatic lockout after 5 failed attempts (15 min)
- 👤 **User Management** - Registration, login, and session management
- 🛡️ **Protected Endpoints** - All AI features require authentication

### Production-Ready Features
- 📊 **Comprehensive Logging** - Request tracking, error monitoring, audit trails
- ⚙️ **Configuration Management** - Environment-based settings
- 🏗️ **Modular Architecture** - Clean separation of concerns
- 📝 **API Documentation** - Interactive Swagger UI at `/docs`

## 🚀 Quickstart
 
### 1. Setup Environment

```bash
# Clone the repository
cd genai-platform-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: Run automated setup for security features
python setup_security.py
```

> **Note**: The `setup_security.py` script will:
> - Install email-validator package
> - Create a sample .env file (if needed)
> - Migrate database to add security fields

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///./genai.db

# JWT Authentication (⚠️ CHANGE IN PRODUCTION!)
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
JWT_REFRESH_EXPIRE_DAYS=30

# Security Settings
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=15

# LLM Provider
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
OLLAMA_TEMPERATURE=0.7

# Vector Store
VECTOR_STORE_TYPE=chroma
VECTOR_STORE_PATH=./chroma_db

# Optional: Other Providers
# OPENAI_API_KEY=your-openai-key
# HUGGINGFACE_API_KEY=your-hf-key
# AWS credentials for Bedrock
```

### 3. Run the Application

```bash
# Option 1: Using the run script
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload

# The server will start at http://127.0.0.1:8000
```

### 4. Access API Documentation

Open your browser to:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📁 Project Structure

```
genai-platform-backend/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── api/v1/                 # API endpoints
│   │   ├── auth.py            # Authentication (register/login)
│   │   ├── chat.py            # Chat endpoints
│   │   ├── rag.py             # RAG endpoints
│   │   └── health.py          # Health check
│   ├── core/                   # Core functionality
│   │   ├── auth.py            # JWT authentication dependency
│   │   ├── config.py          # Configuration management
│   │   ├── logging.py         # Logging setup
│   │   └── security.py        # Password & JWT utilities
│   ├── models/                 # Data models
│   │   ├── chat.py            # Chat request/response models
│   │   ├── rag.py             # RAG models
│   │   └── user.py            # User database model
│   ├── services/               # Business logic
│   │   ├── auth_service.py    # Authentication logic
│   │   ├── chat_service.py    # Chat orchestration
│   │   └── rag_service.py     # RAG orchestration
│   ├── providers/              # LLM provider integrations
│   │   ├── base.py            # Base provider interface
│   │   ├── factory.py         # Provider factory
│   │   ├── ollama.py          # Ollama integration
│   │   ├── openai.py          # OpenAI integration
│   │   ├── huggingface.py     # HuggingFace integration
│   │   └── bedrock.py         # AWS Bedrock integration
│   ├── rag/                    # RAG components
│   │   ├── chunking.py        # Text chunking
│   │   ├── embeddings.py      # Embedding generation
│   │   ├── pipeline.py        # RAG pipeline
│   │   ├── retriever.py       # Document retrieval
│   │   ├── schemas.py         # RAG schemas
│   │   ├── vector_store.py    # Vector storage
│   │   └── ingestion/
│   │       └── pdf_loader.py  # PDF loading
│   └── db/                     # Database
│       ├── session.py         # Database session
│       └── deps.py            # Database dependencies
├── logs/                       # Application logs
├── chroma_db/                  # Vector database
├── requirements.txt            # Python dependencies
├── run.py                      # Application launcher
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── LOGGING.md                  # Logging documentation
├── AUTHENTICATION.md           # Auth testing guide
└── AUTH_COMPLETE_GUIDE.md      # Comprehensive auth tutorial
```

## 🔐 Authentication 

### Register a New User

```bash
POST /api/v1/auth/register
Content-Type: application/x-www-form-urlencoded

email=user@example.com
password=SecureP@ss123
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character (!@#$%^&*...)

### Login

```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

email=user@example.com
password=SecureP@ss123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header for protected endpoints:

```bash
Authorization: Bearer <your_token>
```

## 📡 API Endpoints

### Public Endpoints (No Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login (returns access & refresh tokens) |
| POST | `/api/v1/auth/refresh` | Refresh access token using refresh token |

### Protected Endpoints (Require Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Chat completion |
| POST | `/api/v1/chat/stream` | Streaming chat (SSE) |
| POST | `/api/v1/rag/query` | Query vector store |
| POST | `/api/v1/rag/pdf` | RAG from uploaded PDF |
| POST | `/api/v1/rag/pdf/stream` | Streaming RAG from PDF |
| POST | `/api/v1/rag/ingest/pdf` | Ingest PDF into vector store |

## 💬 API Usage Examples

### Chat Completion

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is Python?",
    "history": [],
    "context": null
  }'
```

### Streaming Chat

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tell me a story",
    "history": [],
    "context": null
  }'
```

### RAG Query

```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "query=What are the key findings?" \
  -F "top_k=5"
```

### PDF Ingestion

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ingest/pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

## 📊 Logging

All application events are logged to the `logs/` directory:

| Log File | Purpose |
|----------|---------|
| `logs/app.log` | Application startup and shutdown |
| `logs/auth.log` | Authentication events |
| `logs/auth_service.log` | Auth service operations |
| `logs/chat.log` | Chat endpoint activity |
| `logs/chat_service.log` | Chat service operations |
| `logs/rag.log` | RAG endpoint activity |
| `logs/rag_service.log` | RAG service operations |
| `logs/ollama.log` | Ollama provider interactions |
| `logs/pdf_loader.log` | PDF processing |

**View logs in real-time:**
```bash
# Tail all logs
tail -f logs/*.log

# Specific log file
tail -f logs/auth.log
```

For detailed logging information, see [LOGGING.md](LOGGING.md)

## 🧪 Testing

### Using Swagger UI

1. Go to http://localhost:8000/docs
2. Register a user via `/api/v1/auth/register`
3. Login via `/api/v1/auth/login` and copy the token
4. Click **"Authorize"** 🔓 button at top
5. Paste token and click **"Authorize"**
6. Test any protected endpoint!

### Using cURL

```bash
# 1. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -d "email=test@example.com&password=TestP@ss123"

# 2. Login and save token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "email=test@example.com&password=TestP@ss123" \
  | jq -r '.access_token')

# 3. Use token
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello!","history":[],"context":null}'
```

## 🔧 Configuration

### Supported LLM Providers

- **Ollama** (default) - Local LLM inference
- **OpenAI** - GPT models via API
- **Hugging Face** - Various models via API
- **AWS Bedrock** - Claude, Titan, etc.

Change provider in `.env`:
```env
LLM_PROVIDER=ollama  # or 'openai', 'huggingface', 'bedrock'
```

### Vector Store Options

- **ChromaDB** (default) - Persistent vector storage
- **In-Memory** - Temporary storage (resets on restart)

```env
VECTOR_STORE_TYPE=chroma  # or 'memory'
VECTOR_STORE_PATH=./chroma_db
```

## 🛡️ Security Best Practices

### Production Deployment

1. **Change JWT Secret Key**:
   ```bash
   # Generate secure key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use HTTPS**: Always use TLS/SSL certificates in production

3. **Environment Variables**: Never commit `.env` to version control

4. **Database**: Use PostgreSQL or MySQL instead of SQLite

5. **Rate Limiting**: Implement request rate limiting per user

6. **Monitoring**: Set up error tracking (Sentry, etc.)

## 📚 Documentation

- **[SECURITY_FEATURES.md](SECURITY_FEATURES.md)** - Security features guide (email validation, refresh tokens, rate limiting, account lockout)
- **[AUTHENTICATION.md](AUTHENTICATION.md)** - Quick authentication testing guide
- **[AUTH_COMPLETE_GUIDE.md](AUTH_COMPLETE_GUIDE.md)** - Comprehensive auth tutorial
- **[LOGGING.md](LOGGING.md)** - Logging system documentation
- **[/docs](http://localhost:8000/docs)** - Interactive API documentation (Swagger)

## 🐛 Troubleshooting

### Common Issues

**Issue: "Not authenticated"**
- Solution: Make sure you included `Authorization: Bearer <token>` header

**Issue: "Invalid or expired token"**
- Solution: Login again to get a new token (access tokens expire after 60 minutes)
- Alternative: Use refresh token to get new access token without re-logging in

**Issue: "Invalid email format"**
- Solution: Ensure email follows standard format (e.g., user@example.com)

**Issue: "Password must contain..."**
- Solution: Use a strong password meeting all requirements (8+ chars, uppercase, lowercase, digit, special char)

**Issue: "Account locked due to failed login attempts"**
- Solution: Wait 15 minutes for automatic unlock, or contact admin
- Cause: 5 failed login attempts in a row

**Issue: "Invalid refresh token"**
- Solution: Refresh tokens expire after 30 days - login again to get new tokens

**Issue: Ollama connection refused**
- Solution: Make sure Ollama is running (`ollama serve`)

### Debug Mode

Enable detailed logging:
```python
# In app/core/logging.py
logger = setup_logger(__name__, log_file="logs/app.log", level=logging.DEBUG)
```

## 🚦 Development Workflow

### Running with Auto-Reload

```bash
uvicorn app.main:app --reload --log-level debug
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Code Formatting

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Guidelines:**
- Keep changes small and focused
- Add tests for new features
- Update documentation
- Follow existing code style
- Write clear commit messages

## 📝 License

No License yet - All rights reserved

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Ollama for local LLM inference
- ChromaDB for vector storage
- The open-source community

---

**Built with ❤️ for the GenAI Platform**
