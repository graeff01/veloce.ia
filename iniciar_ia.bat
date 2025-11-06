@echo off
title Veloce.IA - Iniciando ambiente
echo ============================================
echo 🚀 Iniciando Veloce.IA (Backend + Baileys)
echo ============================================

:: Caminho do projeto
cd /d "C:\Users\Auxiliadora Predial\Desktop\veloce-ia"

:: Ativar ambiente virtual
call backend\venv\Scripts\activate

:: Abrir o backend (FastAPI) em uma nova janela
start cmd /k "cd backend && uvicorn app.main:app --reload"

:: Esperar alguns segundos antes de abrir o Baileys
timeout /t 5 /nobreak >nul

:: Abrir o Baileys em outra janela
start cmd /k "cd backend\app\services\baileys_instance && node index.js"

echo ✅ Tudo pronto! Veloce.IA está rodando.
pause
