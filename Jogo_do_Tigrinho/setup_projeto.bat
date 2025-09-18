@echo off
cd /d %~dp0
echo ========================================
echo 🔧 Criando ambiente virtual do projeto...
echo ========================================
python -m venv venv

echo ========================================
echo 🚀 Ativando ambiente virtual...
echo ========================================
call venv\Scripts\activate.bat

echo ========================================
echo 📦 Instalando dependências...
echo ========================================
pip install matplotlib

echo ========================================
echo 📝 Gerando requirements.txt...
echo ========================================
pip freeze > requirements.txt

echo.
echo ✅ Ambiente configurado com sucesso!
echo.
echo ▶️ Agora você pode rodar seu script Python normalmente.
pause
