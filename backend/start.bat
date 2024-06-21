set PYTHONPATH=%PYTHONPATH%;%~dp0src
python -m uvicorn src.main:app --host 0.0.0.0 --port 46020
echo.
pause