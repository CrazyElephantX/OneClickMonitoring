:: 7. Windows batch скрипт для Windows пользователей
@echo off
REM Автоматическая установка для Windows

echo ================================================
echo   Установка окружения Kibana + Grafana
echo ================================================
echo.

REM Проверка Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker не установлен!
    echo Установите Docker Desktop: https://docs.docker.com/desktop/windows/install/
    pause
    exit /b 1
)
echo [OK] Docker установлен

REM Проверка Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose не установлен!
    pause
    exit /b 1
)
echo [OK] Docker Compose установлен

echo.
echo Создание директорий...
mkdir elk-demo\\logstash-pipeline 2>nul
mkdir elk-demo\\sample-logs 2>nul
mkdir grafana-demo\\prometheus 2>nul
mkdir grafana-demo\\grafana\\provisioning\\datasources 2>nul
mkdir grafana-demo\\grafana\\provisioning\\dashboards 2>nul
echo [OK] Директории созданы

echo.
echo Запуск Linux скрипта через Docker...
echo.
echo ВНИМАНИЕ: На Windows рекомендуется использовать WSL2 и bash скрипт setup.sh
echo.

pause

REM Альтернативный способ - через Git Bash
if exist "C:\\Program Files\\Git\\bin\\bash.exe" (
    "C:\\Program Files\\Git\\bin\\bash.exe" setup.sh
) else (
    echo Git Bash не найден.
    echo Установите Git для Windows: https://git-scm.com/download/win
    echo Затем запустите: bash setup.sh
    pause
)