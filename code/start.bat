@echo off
echo.
echo =====================================================
echo   ProofLayer - AI Compliance Engine
echo   c0mpiled-10/DC: AI for Government Hackathon
echo =====================================================
echo.

:: Check for .env file
if not exist backend\.env (
    echo [!] No .env file found. Creating template...
    echo OPENAI_API_KEY=sk-your-key-here> backend\.env
    echo ANTHROPIC_API_KEY=sk-ant-your-key-here>> backend\.env
    echo OLLAMA_BASE_URL=http://localhost:11434>> backend\.env
    echo.
    echo [!] Edit backend\.env with your API keys, then re-run this script.
    pause
    exit /b 1
)

:: Install dependencies
echo [1/3] Installing Python dependencies...
pip install -r backend\requirements.txt -q

:: Start backend in new window
echo [2/3] Starting backend (http://localhost:8000)...
start "ProofLayer Backend" cmd /k "cd backend && python -m dotenv.cli -f .env run python main.py"

:: Wait for backend
timeout /t 3 /nobreak > nul

:: Open frontend
echo [3/3] Opening frontend...
start "" "frontend\index.html"

echo.
echo ProofLayer is running!
echo   API:  http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo   UI:   frontend\index.html (also at http://localhost:8000/app)
echo.
pause
