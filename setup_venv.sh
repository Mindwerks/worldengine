#!/usr/bin/env bash

# WorldEngine Development Environment Setup Script
# Compatible with Linux and macOS
# Requires: pyenv

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.14"
VENV_DIR="venv"

echo -e "${GREEN}=== WorldEngine Development Environment Setup ===${NC}"

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo -e "${RED}Error: pyenv is not installed.${NC}"
    echo "Please install pyenv first:"
    echo "  macOS: brew install pyenv"
    echo "  Linux: curl https://pyenv.run | bash"
    echo ""
    echo "Then add to your shell configuration (~/.bashrc, ~/.zshrc):"
    echo '  export PYENV_ROOT="$HOME/.pyenv"'
    echo '  export PATH="$PYENV_ROOT/bin:$PATH"'
    echo '  eval "$(pyenv init --path)"'
    echo '  eval "$(pyenv init -)"'
    exit 1
fi

echo -e "${GREEN}✓ pyenv found${NC}"

# Check if protoc is installed
if ! command -v protoc &> /dev/null; then
    echo -e "${YELLOW}Warning: protoc (Protocol Buffer Compiler) is not installed.${NC}"
    echo "protoc is required to regenerate protobuf files."
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            echo -e "${YELLOW}Installing protobuf via Homebrew...${NC}"
            brew install protobuf
            echo -e "${GREEN}✓ protobuf installed${NC}"
        else
            echo "Please install protobuf:"
            echo "  brew install protobuf"
            echo "or download from: https://github.com/protocolbuffers/protobuf/releases"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Please install protobuf compiler:"
        echo "  Debian/Ubuntu: sudo apt-get install -y protobuf-compiler"
        echo "  Fedora/RHEL: sudo dnf install protobuf-compiler"
        echo "  or download from: https://github.com/protocolbuffers/protobuf/releases"
        read -p "Press Enter to continue or Ctrl+C to cancel..."
    fi
else
    PROTOC_VERSION=$(protoc --version | awk '{print $2}')
    echo -e "${GREEN}✓ protoc found (version ${PROTOC_VERSION})${NC}"
fi

# Check if Python 3.14 is available in pyenv
AVAILABLE_VERSIONS=$(pyenv install --list | grep -E "^\s*${PYTHON_VERSION}" | head -1 | xargs)

if [ -z "$AVAILABLE_VERSIONS" ]; then
    echo -e "${YELLOW}Warning: Python ${PYTHON_VERSION} not yet available in pyenv.${NC}"
    echo "Attempting to find the latest Python 3.14 release..."
    AVAILABLE_VERSIONS=$(pyenv install --list | grep -E "^\s*3\.14\.[0-9]+" | tail -1 | xargs)

    if [ -z "$AVAILABLE_VERSIONS" ]; then
        echo -e "${RED}Error: Python 3.14.x not available in pyenv.${NC}"
        echo "Please update pyenv: cd \$(pyenv root) && git pull"
        exit 1
    fi
    PYTHON_VERSION="$AVAILABLE_VERSIONS"
fi

echo -e "${GREEN}Found Python version: ${PYTHON_VERSION}${NC}"

# Check if Python version is already installed
if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}$"; then
    echo -e "${YELLOW}Installing Python ${PYTHON_VERSION}...${NC}"
    echo "This may take a few minutes..."

    # Install dependencies based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS"
        if command -v brew &> /dev/null; then
            echo "Ensuring build dependencies are available..."
            brew install openssl readline sqlite3 xz zlib 2>/dev/null || true
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Detected Linux"
        echo "Make sure you have build dependencies installed:"
        echo "  Debian/Ubuntu: sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \\"
        echo "    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \\"
        echo "    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git"
        echo ""
        read -p "Press Enter to continue or Ctrl+C to cancel..."
    fi

    pyenv install ${PYTHON_VERSION}
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} installed${NC}"
else
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} already installed${NC}"
fi

# Set local Python version
echo -e "${YELLOW}Setting local Python version to ${PYTHON_VERSION}...${NC}"
pyenv local ${PYTHON_VERSION}

# Verify Python version
CURRENT_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Active Python version: ${CURRENT_VERSION}${NC}"

# Remove existing venv if it exists
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf "$VENV_DIR"
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python -m venv "$VENV_DIR"
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip, setuptools, and wheel
echo -e "${YELLOW}Upgrading pip, setuptools, and wheel...${NC}"
pip install --upgrade pip setuptools wheel

# Install requirements
echo -e "${YELLOW}Installing dependencies...${NC}"

# Install package in development mode with all dependencies
if [ -f "pyproject.toml" ]; then
    echo "Installing worldengine with dependencies from pyproject.toml..."
    pip install -e ".[hdf5,dev]"
fi

# Regenerate protobuf files if protoc is available
if command -v protoc &> /dev/null; then
    echo -e "${YELLOW}Regenerating protobuf files...${NC}"
    cd worldengine && protoc World.proto --python_out=protobuf && cd ..
    echo -e "${GREEN}✓ Protobuf files regenerated${NC}"
else
    echo -e "${YELLOW}Skipping protobuf regeneration (protoc not available)${NC}"
fi

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Virtual environment created in: $VENV_DIR"
echo "Python version: $CURRENT_VERSION"
echo ""
echo "To activate the virtual environment, run:"
echo -e "${YELLOW}  source $VENV_DIR/bin/activate${NC}"
echo ""
echo "To deactivate when done:"
echo -e "${YELLOW}  deactivate${NC}"
echo ""
echo "To run tests:"
echo -e "${YELLOW}  pytest tests/${NC}"
echo ""
echo "To start development:"
echo -e "${YELLOW}  worldengine --help${NC}"
