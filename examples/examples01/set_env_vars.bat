@echo off
REM Batch script to set EGS environment variables
REM Run this script before using the workspace management scripts

set EGS_ENDPOINT=http://35.229.87.139:8080
set EGS_API_KEY=0afc6c1e-30a4-4058-a0de-23e3c75d9933

echo ✅ Environment variables set successfully!
echo EGS_ENDPOINT: %EGS_ENDPOINT%
echo EGS_API_KEY: %EGS_API_KEY%
echo.
echo You can now run the workspace management scripts:
echo   - python create_workspace.py --config workspace_config.yaml
echo   - python update_workspace.py --config update_workspace_config.yaml
echo   - python delete_workspace.py --config workspace_config.yaml 