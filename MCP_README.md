# MCP WhatsApp Server

A Model Context Protocol (MCP) server for WhatsApp messaging with OAuth authentication, Excel upload handling, and rate limiting.

## Features

- **OAuth Authentication**: User-based client credentials with secure token generation
- **Excel Upload**: Process Excel files to extract phone numbers
- **Rate Limiting**: 429 HTTP responses with configurable limits
- **Batch Sending**: Send messages to thousands of phone numbers
- **Message Templates**: Customizable message templates for bulk messaging

## Installation

```bash
pip install -r mcp_requirements.txt
```

## Configuration

Copy the example environment file and configure:

```bash
cp mcp_env.example .env
# Edit .env with your settings
```

## Quick Start

```bash
python mcp_server.py
```

The server will start on `http://localhost:8001`

## API Endpoints

### 1. Register OAuth Client

Register OAuth client credentials for a user:

```bash
curl -X POST "http://localhost:8001/api/oauth/register?user_id=user123" \
  -d "grant_type=client_credentials" \
  -d "scope=whatsapp_message" \
  -d "redirect_uri=http://yourapp.com/callback"
```

**Response:**
```json
{
  "message": "OAuth client registered successfully",
  "client_id": "a1b2c3d4e5f6...",
  "client_secret": "z9y8x7w6v5u4...",
  "grant_type": "client_credentials",
  "scope": "whatsapp_message"
}
```

### 2. Upload Excel File

Upload an Excel file with phone numbers:

```bash
curl -X POST "http://localhost:8001/api/upload/excel?user_id=user123" \
  -d "file_path=/path/to/phone_numbers.xlsx"
```

**Response:**
```json
{
  "batch_id": "uuid-here",
  "phones": ["9876543210", "9876543211", ...],
  "total_phones": 1000,
  "message": "Successfully uploaded 1000 phone numbers"
}
```

### 3. Send Messages

Send messages to the uploaded phone numbers:

```bash
curl -X POST "http://localhost:8001/api/messages/send?user_id=user123" \
  -d "batch_id=uuid-here" \
  -d "message_template=Hi there! This is a test message."
```

**Response:**
```json
{
  "batch_id": "uuid-here",
  "total_phones": 1000,
  "sent": 1000,
  "results": [
    {
      "phone": "9876543210",
      "status": "sent",
      "message_id": "msg_uuid_1",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    ...
  ],
  "message": "Message template 'Hi there! This is a test message.' would be sent to 1000 phone numbers"
}
```

### 4. Check Rate Limit

Check current rate limit status:

```bash
curl "http://localhost:8001/api/rate-limit/check?user_id=user123"
```

**Response:**
```json
{
  "allowed": true,
  "code": 200,
  "message": "Request allowed",
  "current_requests": 3,
  "limit": 10,
  "window": 60
}
```

### 5. Get Batch Status

Check the status of a batch:

```bash
curl "http://localhost:8001/api/batch/uuid-here?user_id=user123"
```

**Response:**
```json
{
  "batch_id": "uuid-here",
  "phones_count": 1000,
  "uploaded_at": "2024-01-01T12:00:00Z",
  "file_size": 1024
}
```

## Rate Limiting

The server implements rate limiting with the following configuration:

- **Requests per window**: 10 requests per 60 seconds
- **Burst limit**: 3 concurrent requests per window
- **429 HTTP responses**: When limits are exceeded

### Rate Limit Exceeded Response:

```json
{
  "allowed": false,
  "code": 429,
  "message": "Rate limit exceeded. 52 seconds until next request.",
  "retry_after": 52,
  "current_requests": 10,
  "limit": 10,
  "window": 60
}
```

## Excel File Format

The Excel file should contain phone numbers in any column:

```
Column A    Column B    Column C
9876543210  9876543211  9876543212
9876543213  9876543214  9876543215
```

The server automatically extracts all valid phone numbers (10+ digits) from all sheets.

## MCP Integration

The server implements MCP protocol for direct integration with AI assistants:

### Initialize MCP Connection:

```bash
curl -X POST "http://localhost:8001/mcp/init?user_id=user123"
```

### Process MCP Command:

```bash
curl -X POST "http://localhost:8001/mcp/process" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "command": "upload_excel",
    "params": {"file_path": "/path/to/phone_numbers.xlsx"}
  }'
```

## Security Features

- **OAuth Client Credentials**: Secure random client ID and secret generation
- **Rate Limiting**: Prevents abuse and rate limit attacks
- **File Size Limits**: Maximum 10MB for Excel files
- **Phone Number Limits**: Maximum 5000 phones per Excel file
- **Batch Size Limits**: Maximum 1000 phones per send operation

## Docker Support

The server can be run in Docker:

```bash
docker build -t mcp-whatsapp-server .
docker run -p 8001:8001 --env-file .env mcp-whatsapp-server
```

## Environment Variables

- `MCP_HOST`: Server host (default: 0.0.0.0)
- `MCP_PORT`: Server port (default: 8001)
- `RATE_LIMIT_WINDOW`: Rate limit window in seconds (default: 60)
- `RATE_LIMIT_REQUESTS`: Requests per window (default: 10)
- `RATE_LIMIT_BURST`: Burst limit (default: 3)
- `MAX_EXCEL_SIZE`: Maximum Excel file size in bytes (default: 10MB)
- `MAX_PHONES_PER_FILE`: Maximum phones per Excel file (default: 5000)
- `MAX_BATCH_SIZE`: Maximum phones per send (default: 1000)

## Troubleshooting

### Rate Limit Exceeded

If you receive a 429 error, wait for the `retry_after` seconds before trying again.

### Excel Upload Failed

- Check that the file exists at the specified path
- Ensure the file size is under 10MB
- Verify the file contains valid phone numbers (10+ digits)

### OAuth Not Working

- Register OAuth client first using the register endpoint
- Make sure to use the correct user_id
- Check that client_secret is kept secret

## Integration with Existing Whatfy App

This MCP server can be integrated with the existing Whatfy FastAPI application for WhatsApp messaging functionality.

### Integration Steps:

1. Deploy this MCP server on a separate port
2. Update the Whatfy app to call the MCP server endpoints
3. Use the OAuth client credentials from the MCP server
4. Upload Excel files via MCP upload endpoint
5. Send messages using the MCP send endpoint
