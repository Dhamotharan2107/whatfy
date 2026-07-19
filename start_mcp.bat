@echo off
echo ========================================
echo MCP WhatsApp Server - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r mcp_requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Starting MCP Server...
echo Server will run on http://localhost:8001
echo Press Ctrl+C to stop the server
echo.

REM Start the MCP server
python mcp_server.py

pause
