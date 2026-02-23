# Logging Documentation

## Overview

Comprehensive logging has been implemented throughout the GenAI Platform Backend to improve observability, debugging, and monitoring.

## Logging Architecture

### Logger Setup
 
All loggers are configured using the centralized `setup_logger` function from [app/core/logging.py](app/core/logging.py):

```python
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/module.log")
```

### Log Levels

- **DEBUG**: Detailed diagnostic information (prompt lengths, token counts, internal state)
- **INFO**: General informational messages (successful operations, initialization)
- **WARNING**: Warning messages (authentication failures, skipped operations, client disconnects)
- **ERROR**: Error messages with full stack traces (exceptions, failures)

## Log Files

All logs are stored in the `logs/` directory:

| Log File | Purpose |
|----------|---------|
| `logs/app.log` | Application startup, middleware configuration, router registration |
| `logs/auth.log` | Authentication API endpoints (login, register) |
| `logs/auth_service.log` | Authentication service operations |
| `logs/chat.log` | Chat API endpoints (streaming and non-streaming) |
| `logs/chat_service.log` | Chat service operations |
| `logs/rag.log` | RAG API endpoints (query, PDF ingestion, streaming) |
| `logs/rag_service.log` | RAG service operations |
| `logs/ollama.log` | Ollama provider interactions |
| `logs/pdf_loader.log` | PDF loading and text extraction |

## Logged Events

### Application Lifecycle
- Application initialization
- CORS middleware configuration
- Router registration
- Startup and shutdown events

### Authentication
- Registration attempts (success/failure)
- Login attempts (success/failure)
- Email validation
- Token generation
- Database errors

### Chat Operations
- Request received (prompt length, history size)
- Response generation (success/failure)
- Streaming events (token count, disconnects)
- Provider errors

### RAG Operations
- Vector store queries (query text, top_k, results)
- PDF uploads (filename, file size)
- PDF processing (pages extracted, chunks created)
- Document ingestion (chunks added, duplicates skipped)
- Embedding generation
- Retrieval operations
- Temporary file cleanup

### AI Provider (Ollama)
- Model configuration (model name, temperature)
- Generation requests (prompt length, context usage)
- Streaming operations (token count)
- API errors

### PDF Processing
- File loading (page count)
- Text extraction
- Processing errors

## Log Format

All logs follow a consistent format:

```
YYYY-MM-DD HH:MM:SS - module_name - LEVEL - message
```

Example:
```
2026-02-12 14:30:15 - app.services.chat_service - INFO - Response generated successfully - length: 245
```

## Log Rotation

Logs are automatically rotated to prevent disk space issues:
- Maximum file size: 10MB
- Backup count: 5 files
- Old logs are automatically compressed and archived

## Best Practices

### What is Logged
✅ Request/response metadata (sizes, counts)
✅ Success/failure of operations
✅ Authentication attempts
✅ Database operations
✅ File operations
✅ API errors with stack traces
✅ Performance metrics (token counts, chunk counts)

### What is NOT Logged
❌ Passwords or sensitive credentials
❌ Full request/response bodies (only metadata)
❌ Personal user data (only email for auth events)
❌ Full context/prompts (only lengths for DEBUG level)

## Monitoring

### Key Metrics to Monitor

1. **Error Rates**:
   ```bash
   grep "ERROR" logs/*.log | wc -l
   ```

2. **Authentication Failures**:
   ```bash
   grep "Authentication failed" logs/auth_service.log
   ```

3. **RAG Performance**:
   ```bash
   grep "chunks" logs/rag_service.log
   ```

4. **API Usage**:
   ```bash
   grep "request received" logs/*.log
   ```

## Development vs Production

### Development
- Log level: DEBUG
- Console output: Enabled
- File logging: Enabled
- Full stack traces: Yes

### Production (Recommended)
- Log level: INFO
- Console output: Enabled (for container logs)
- File logging: Enabled
- Full stack traces: Yes (for ERROR level)

To change log level, modify the `setup_logger` call:

```python
logger = setup_logger(__name__, log_file="logs/app.log", level=logging.INFO)
```

## Troubleshooting

### No Logs Appearing
1. Check that `logs/` directory exists
2. Verify file permissions
3. Check console output for logger initialization messages

### Large Log Files
- Logs auto-rotate at 10MB
- Check backup count setting
- Consider implementing log aggregation for production

### Missing Context
- Increase log level to DEBUG for more details
- Check specific log files for module-specific events

## Integration with Monitoring Tools

The logging format is compatible with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **CloudWatch** (AWS)
- **Application Insights** (Azure)
- **Datadog**

Configure log shipping based on your deployment platform.

## Future Enhancements

- [ ] Structured JSON logging for better parsing
- [ ] Request ID tracking across services
- [ ] Performance timing metrics
- [ ] User session tracking
- [ ] Log aggregation configuration
- [ ] Metrics export (Prometheus)
