@echo off
echo ============================================
echo   Karbon Salınımı Projesi - Başlatıcı
echo ============================================
echo.

REM 1. Python bağımlılıklarını yükle
echo [1/4] Python bağımlılıkları yükleniyor...
pip install fastapi uvicorn python-multipart pdfplumber pandas openpyxl python-dotenv --quiet 2>nul
if %errorlevel% neq 0 (
    echo HATA: pip install başarısız. Python yüklü mü?
    pause
    exit /b 1
)
echo ✓ Python bağımlılıkları tamam.

REM 2. Frontend bağımlılıklarını yükle
echo [2/4] Frontend bağımlılıkları kontrol ediliyor...
cd frontend
if not exist node_modules (
    echo    npm install çalıştırılıyor...
    npm install --silent
)
npm install --save-dev @types/node --silent 2>nul
echo ✓ Frontend bağımlılıkları tamam.

REM 3. Frontend'i build et
echo [3/4] Frontend build ediliyor...
call npm run build
if %errorlevel% neq 0 (
    echo HATA: Frontend build başarısız.
    pause
    exit /b 1
)
echo ✓ Frontend build tamam.

REM 4. Sunucuyu başlat
cd ..
echo [4/4] Sunucu başlatılıyor...
echo.
echo ============================================
echo   http://localhost:8000 adresinde açılıyor
echo   Durdurmak için Ctrl+C basın
echo ============================================
echo.
python api.py
