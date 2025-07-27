#!/bin/bash

echo "========================================"
echo "       ussh Setup Script (macOS/Linux)  "
echo "========================================"

# OS 감지
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "Error: Unsupported OS. This script is for macOS and Linux only."
    exit 1
fi

echo "Detected OS: $OS"

# 1. uv 설치
echo ""
echo "Installing uv..."

if [[ "$OS" == "macos" ]]; then
    # macOS: Homebrew로 설치 시도
    if command -v brew &> /dev/null; then
        brew install uv
    else
        echo "Homebrew not found. Installing uv with curl..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
else
    # Linux: curl로 설치
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# uv 설치 확인
if command -v uv &> /dev/null; then
    echo "✓ uv installed successfully"
else
    echo "✗ Failed to install uv"
    exit 1
fi

# 2. git-crypt 설치
echo ""
echo "Installing git-crypt..."

if [[ "$OS" == "macos" ]]; then
    # macOS: Homebrew로 설치
    if command -v brew &> /dev/null; then
        brew install git-crypt
    else
        echo "Error: Homebrew is required to install git-crypt on macOS"
        echo "Please install Homebrew first: https://brew.sh"
        exit 1
    fi
else
    # Linux: 패키지 매니저 감지 및 설치
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y git-crypt
    elif command -v yum &> /dev/null; then
        sudo yum install -y git-crypt
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y git-crypt
    else
        echo "Error: No supported package manager found (apt, yum, dnf)"
        exit 1
    fi
fi

# git-crypt 설치 확인
if command -v git-crypt &> /dev/null; then
    echo "✓ git-crypt installed successfully"
else
    echo "✗ Failed to install git-crypt"
    exit 1
fi

# 3. 가상환경 생성
echo ""
echo "Creating virtual environment..."

if [ ! -d ".venv" ]; then
    uv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# 4. 가상환경 활성화 및 ussh 설치
echo ""
echo "Installing ussh..."

# 가상환경 활성화
source .venv/bin/activate

# ussh 설치
uv pip install -e .

# 설치 확인
if .venv/bin/ussh --help &> /dev/null; then
    echo "✓ ussh installed successfully"
else
    echo "✗ Failed to install ussh"
    exit 1
fi

# 5. git-crypt 초기화
echo ""
echo "Initializing git-crypt..."
git-crypt init 2>/dev/null || echo "git-crypt already initialized"

echo ""
echo "========================================"
echo "         Setup completed!               "
echo "========================================"
echo ""
echo "To use ussh, activate the virtual environment:"
echo "  source .venv/bin/activate"
echo ""
echo "Then you can use:"
echo "  ussh --help"
echo ""