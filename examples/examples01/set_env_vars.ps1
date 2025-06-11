# PowerShell script to set EGS environment variables
# Run this script before using the workspace management scripts

$env:EGS_ENDPOINT = "http://35.229.87.139:8080"
$env:EGS_API_KEY = "0afc6c1e-30a4-4058-a0de-23e3c75d9933"

Write-Host "✅ Environment variables set successfully!" -ForegroundColor Green
Write-Host "EGS_ENDPOINT: $env:EGS_ENDPOINT" -ForegroundColor Cyan
Write-Host "EGS_API_KEY: $env:EGS_API_KEY" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run the workspace management scripts:" -ForegroundColor Yellow
Write-Host "  - python create_workspace.py --config workspace_config.yaml"
Write-Host "  - python update_workspace.py --config update_workspace_config.yaml"
Write-Host "  - python delete_workspace.py --config workspace_config.yaml" 