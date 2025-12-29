@echo off
echo Configurando entorno...

if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

echo Activando entorno virtual...
call venv\Scripts\activate

echo Instalando dependencias...
pip install -r requirements.txt

echo Iniciando aplicacion...
streamlit run app/main.py

pause
