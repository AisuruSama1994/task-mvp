@echo off
REM Arranque de Task MVP (Sistema de Recordatorios) en Windows: backend
REM (FastAPI/Uvicorn) + frontend (Vite). Igual que Apolo-Avalian y Claudia:
REM el backend y la base de datos (Postgres, en esta misma PC) se hablan
REM por 127.0.0.1.
REM
REM Para parar todo: stop-task-mvp.bat

cd /d "D:\task-mvp\backend"
start "Task-MVP Backend" /min cmd /k "venv\Scripts\python.exe main.py"

cd /d "D:\task-mvp\frontend"
start "Task-MVP Frontend" /min cmd /k "npm run dev"

echo.
echo == Task MVP arrancando ==
echo Backend:  http://127.0.0.1:8040
echo Frontend: http://localhost:5174
echo.
echo Si algo no arranca, mira las ventanas minimizadas "Task-MVP Backend" y "Task-MVP Frontend".
