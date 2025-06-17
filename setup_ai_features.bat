@echo off
echo ================================================
echo  ResourcePro AI Features Setup
echo ================================================
echo.

echo 1. Installing required Python packages...
pip install python-dotenv>=1.0.0
pip install google-generativeai>=0.3.0

echo.
echo 2. Checking current .env configuration...
if exist .env (
    echo .env file exists!
) else (
    echo ERROR: .env file not found!
    exit /b 1
)

echo.
echo 3. Checking for Gemini API key...
findstr /C:"GEMINI_API_KEY=your_gemini_api_key_here" .env >nul
if %errorlevel% == 0 (
    echo.
    echo ================================================
    echo  IMPORTANT: Configure your Gemini API key!
    echo ================================================
    echo.
    echo 1. Go to: https://aistudio.google.com/app/apikey
    echo 2. Create a new API key
    echo 3. Edit the .env file and replace:
    echo    GEMINI_API_KEY=your_gemini_api_key_here
    echo    with your actual API key
    echo.
    echo Example:
    echo    GEMINI_API_KEY=AIzaSyD1234567890abcdefghijk
    echo.
) else (
    echo Gemini API key appears to be configured!
)

echo.
echo 4. Testing Django configuration...
python manage.py check --settings=resourcepro.settings

echo.
echo 5. Testing AI features availability...
python manage.py test_ai_features --feature skills

echo.
echo ================================================
echo  Setup complete!
echo ================================================
echo.
echo Next steps:
echo 1. Configure your Gemini API key in .env file
echo 2. Run: python manage.py runserver
echo 3. Visit: http://localhost:8000/analytics/ai/
echo.
pause
