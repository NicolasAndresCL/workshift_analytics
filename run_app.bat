@echo off
title Registro de Tareas - Streamlit

echo =====================================
echo    REGISTRO DE TAREAS - STREAMLIT
echo =====================================

:: Ir a la carpeta donde está el .bat
cd /d "%~dp0"

echo.
echo Cambiando al directorio del proyecto...
echo %cd%

echo.
echo Activando entorno virtual...
call env\Scripts\activate

echo.
echo =====================================
echo Iniciando servidor Streamlit...
echo =====================================

:: Abrir navegador
start "" http://localhost:8501

:: Ejecutar aplicación
streamlit run app.py

echo.
echo =====================================
echo Servidor detenido.
echo =====================================
pause
