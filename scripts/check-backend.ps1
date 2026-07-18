# Run backend lint, format check, and tests — same checks as CI.
Set-Location "$PSScriptRoot\..\backend"
& ".\.venv\Scripts\ruff.exe" check . && `
& ".\.venv\Scripts\black.exe" --check . && `
& ".\.venv\Scripts\pytest.exe"
