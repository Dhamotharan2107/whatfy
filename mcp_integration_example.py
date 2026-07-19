"""
Integration Example: How to use MCP WhatsApp Server with Whatfy App
This shows how to integrate the MCP server endpoints with your existing FastAPI application
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os

# MCP Server Configuration
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8001")

# Create API router
mcp_router = APIRouter(prefix="/api/mcp", tags=["MCP Integration"])

# ── Request Models ────────────────────────────────────────────────────────────────
class MCPOAuthRegister(BaseModel):
    """Request model for OAuth registration"""
    grant_type: str = "client_credentials"
    scope: str = "whatsapp_message"
    redirect_uri: str = ""

class MCPOAuthToken(BaseModel):
    """Request model for OAuth token exchange"""
    auth_code: str
    redirect_uri: str = ""

class MCPExcelUpload(BaseModel):
    """Request model for Excel upload"""
    file_path: str

class MCPSendMessages(BaseModel):
    """Request model for sending messages"""
    batch_id: str
    message_template: str = "Hi"
    dry_run: bool = False

# ── MCP Integration Endpoints ─────────────────────────────────────────────────────
@mcp_router.post("/oauth/register")
async def mcp_oauth_register(request: MCPOAuthRegister):
    """
    Register OAuth client credentials via MCP server
    """
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/api/oauth/register",
            params={"user_id": "current_user_id"},  # Replace with actual user_id
            data={
                "grant_type": request.grant_type,
                "scope": request.scope,
                "redirect_uri": request.redirect_uri
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("error", "Failed to register OAuth client")
            )
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Connection to MCP server failed: {str(e)}")

@mcp_router.post("/oauth/token")
async def mcp_oauth_token(request: MCPOAuthToken):
    """
    Exchange authorization code for access token via MCP server
    """
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/api/oauth/token",
            params={"user_id": "current_user_id"},  # Replace with actual user_id
            data={
                "auth_code": request.auth_code,
                "redirect_uri": request.redirect_uri
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("error", "Failed to exchange token")
            )
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Connection to MCP server failed: {str(e)}")

@mcp_router.post("/upload/excel")
async def mcp_upload_excel(request: MCPExcelUpload):
    """
    Upload Excel file and extract phone numbers via MCP server
    """
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/api/upload/excel",
            params={"user_id": "current_user_id"},  # Replace with actual user_id
            data={"file_path": request.file_path}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("error", "Failed to upload Excel file")
            )
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Connection to MCP server failed: {str(e)}")

@mcp_router.post("/messages/send")
async def mcp_send_messages(request: MCPSendMessages):
    """
    Send messages via MCP server
    """
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/api/messages/send",
            params={"user_id": "current_user_id"},  # Replace with actual user_id
            data={
                "batch_id": request.batch_id,
                "message_template": request.message_template,
                "dry_run": request.dry_run
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("error", "Failed to send messages")
            )
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Connection to MCP server failed: {str(e)}")

@mcp_router.get("/batch/{batch_id}")
async def mcp_get_batch_status(batch_id: str):
    """
    Get batch status via MCP server
    """
    try:
        response = requests.get(
            f"{MCP_SERVER_URL}/api/batch/{batch_id}",
            params={"user_id": "current_user_id"}  # Replace with actual user_id
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("error", "Failed to get batch status")
            )
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Connection to MCP server failed: {str(e)}")

@mcp_router.get("/statistics")
async def mcp_get_statistics():
    """
    Get server statistics via MCP server
    """
    try:
        response = requests.get(
            f"{MCP_SERVER_URL}/api/statistics",
            params={"user_id": "current_user_id"}  # Replace with actual user_id
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("error", "Failed to get statistics")
            )
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Connection to MCP server failed: {str(e)}")

# ── Usage Example ────────────────────────────────────────────────────────────────
# In your main FastAPI application:
#
# from fastapi import FastAPI
# app = FastAPI()
#
# # Include the MCP router
# app.include_router(mcp_router)
#
# # Make sure to set the MCP_SERVER_URL environment variable
# # export MCP_SERVER_URL=http://localhost:8001
#
# # Use the endpoints like:
# @app.post("/send-whatsapp-messages")
# async def send_messages(file_path: str, message: str):
#     # Step 1: Upload Excel file
#     upload_response = await mcp_upload_excel(MCPExcelUpload(file_path=file_path))
#     batch_id = upload_response["data"]["batch_id"]
#
#     # Step 2: Send messages
#     send_response = await mcp_send_messages(MCPSendMessages(
#         batch_id=batch_id,
#         message_template=message
#     ))
#
#     return send_response

# ── Example: Batch Message Sending Flow ──────────────────────────────────────────
"""
# Complete Example of Using MCP Integration:

@app.post("/api/send-batch-messages")
async def send_batch_messages(
    file_path: str = Form(...),
    message: str = Form(...),
    current_user_id: str = Header(...)
):
    """
    Upload Excel and send messages in one endpoint
    """
    try:
        # 1. Upload Excel file via MCP
        upload_response = requests.post(
            f"{MCP_SERVER_URL}/api/upload/excel",
            params={"user_id": current_user_id},
            data={"file_path": file_path}
        )
        
        if upload_response.status_code != 200:
            raise HTTPException(
                status_code=upload_response.status_code,
                detail=upload_response.json().get("error", "Upload failed")
            )
        
        batch_id = upload_response.json()["data"]["batch_id"]
        
        # 2. Send messages via MCP
        send_response = requests.post(
            f"{MCP_SERVER_URL}/api/messages/send",
            params={"user_id": current_user_id},
            data={
                "batch_id": batch_id,
                "message_template": message,
                "dry_run": False
            }
        )
        
        if send_response.status_code != 200:
            raise HTTPException(
                status_code=send_response.status_code,
                detail=send_response.json().get("error", "Sending failed")
            )
        
        return send_response.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"MCP Server connection failed: {str(e)}")
"""

if __name__ == "__main__":
    print("""
    MCP Integration Module for Whatfy App
    =======================================

    This module provides integration endpoints for the MCP WhatsApp Server.

    Endpoints Available:
    - POST /api/mcp/oauth/register - Register OAuth client
    - POST /api/mcp/oauth/token - Exchange authorization code for token
    - POST /api/mcp/upload/excel - Upload Excel file
    - POST /api/mcp/messages/send - Send messages to batch
    - GET /api/mcp/batch/{batch_id} - Get batch status
    - GET /api/mcp/statistics - Get server statistics

    Usage:
    1. Set MCP_SERVER_URL environment variable
    2. Include this router in your FastAPI app
    3. Call the endpoints with proper user_id

    Example:
    >>> import requests
    >>> response = requests.post(
    ...     "http://localhost:8001/api/mcp/upload/excel",
    ...     params={"user_id": "user123"},
    ...     data={"file_path": "/path/to/phones.xlsx"}
    ... )
    >>> result = response.json()
    >>> batch_id = result["data"]["batch_id"]
    """)
