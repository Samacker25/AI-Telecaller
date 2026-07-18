# Run the backend locally with auto-reload.
# Prerequisites: python -m venv backend/.venv && backend/.venv/Scripts/pip install -r backend/requirements-dev.txt
Set-Location "$PSScriptRoot\..\backend"
& ".\.venv\Scripts\uvicorn.exe" app.main:app --reload --port 8000
