@echo off
REM Para el backend y el frontend de Task MVP. Cierra por el puerto que usa
REM cada uno (mas confiable que por titulo de ventana).

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8040.*LISTENING"') do taskkill /PID %%p /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5174.*LISTENING"') do taskkill /PID %%p /F >nul 2>&1

taskkill /FI "WINDOWTITLE eq Task-MVP Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Task-MVP Frontend*" /T /F >nul 2>&1

echo Task MVP detenido.
