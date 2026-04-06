@echo off
echo Iniciando BIM Classification Engine...
echo El navegador se abrira automaticamente.
echo Para cerrar la aplicacion, cierra esta ventana.
echo.
python -m streamlit run app.py --server.headless false --browser.gatherUsageStats false
pause
