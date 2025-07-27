# Windows PowerShell Setup Script for ussh

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       ussh Setup Script (Windows)      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. uv 설치
Write-Host ""
Write-Host "Installing uv..." -ForegroundColor Yellow

try {
    irm https://astral.sh/uv/install.ps1 | iex
    Write-Host "✓ uv installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install uv" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# PATH 업데이트를 위해 새로운 PowerShell 세션에서 확인
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# uv 설치 확인
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "✓ uv is available" -ForegroundColor Green
} else {
    Write-Host "✗ uv not found in PATH. Please restart PowerShell and run this script again." -ForegroundColor Red
    exit 1
}

# 2. git-crypt 설치 안내
Write-Host ""
Write-Host "git-crypt installation:" -ForegroundColor Yellow
Write-Host "git-crypt needs to be installed manually on Windows." -ForegroundColor Cyan
Write-Host "1. Download from: https://github.com/AGWA/git-crypt/releases" -ForegroundColor White
Write-Host "2. Extract the zip file" -ForegroundColor White
Write-Host "3. Add the extracted folder to your PATH" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter after installing git-crypt to continue..." -ForegroundColor Yellow
Read-Host

# git-crypt 설치 확인
if (Get-Command git-crypt -ErrorAction SilentlyContinue) {
    Write-Host "✓ git-crypt found" -ForegroundColor Green
} else {
    Write-Host "✗ git-crypt not found. Please install it and add to PATH." -ForegroundColor Red
    exit 1
}

# 3. 가상환경 생성
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow

if (!(Test-Path -Path ".venv")) {
    uv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# 4. 가상환경 활성화 및 ussh 설치
Write-Host ""
Write-Host "Installing ussh..." -ForegroundColor Yellow

# 가상환경 활성화
& .\.venv\Scripts\Activate.ps1

# ussh 설치
uv pip install -e .

# 설치 확인
$installResult = & .\.venv\Scripts\ussh.exe --help 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ ussh installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install ussh" -ForegroundColor Red
    exit 1
}

# 5. git-crypt 초기화
Write-Host ""
Write-Host "Initializing git-crypt..." -ForegroundColor Yellow
git-crypt init 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ git-crypt initialized" -ForegroundColor Green
} else {
    Write-Host "git-crypt already initialized" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "         Setup completed!               " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use ussh, activate the virtual environment:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Then you can use:" -ForegroundColor Yellow
Write-Host "  ussh --help" -ForegroundColor White
Write-Host ""