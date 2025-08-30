@echo off
echo Starting Auto Profit Trader...
echo.

REM Set environment variables to suppress protobuf warnings
set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
set PYTHONWARNINGS=ignore::UserWarning:google.protobuf.runtime_version

REM Set console to UTF-8 encoding for better Unicode support
chcp 65001 > nul

REM Set Python path
set PYTHONPATH=%~dp0src

REM Change to the script directory
cd /d "%~dp0"

echo Environment configured for optimal performance
echo Protobuf warnings suppressed for cleaner output
echo Press Ctrl+C to stop the trader
echo.

REM Start the trader
python trader_daemon.py

pause
