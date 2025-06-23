# PowerShell script to set environment variables for Auto-GPR examples
# Usage: .\set_env_vars.ps1

Write-Host "Setting up environment variables for Auto-GPR examples..." -ForegroundColor Green

# Set the provided environment variables
$env:EGS_ENDPOINT = "http://35.229.87.139:8080"
$env:EGS_API_KEY = "0afc6c1e-30a4-4058-a0de-23e3c75d9933"

Write-Host "✅ EGS_ENDPOINT set to: $env:EGS_ENDPOINT" -ForegroundColor Green
Write-Host "✅ EGS_API_KEY set" -ForegroundColor Green

Write-Host ""
Write-Host "Environment variables configured! You can now run:" -ForegroundColor Green
Write-Host "  python autogpr_e2e_test.py --config autogpr_config.yaml" -ForegroundColor Cyan
Write-Host "  python manage_gpr_templates.py --action list" -ForegroundColor Cyan
Write-Host "  python manage_gpr_bindings.py --action list" -ForegroundColor Cyan

Write-Host ""
Write-Host "Note: These environment variables are set for the current PowerShell session." -ForegroundColor Yellow 