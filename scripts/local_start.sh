#!/bin/bash
# Local Development Startup Script
# M13: Quick start for development

set -e

echo "=========================================="
echo "NL2SQL Local Development Server"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check .env
if [ ! -f .env ]; then
    print_warning ".env not found, creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please edit .env and add your API keys"
        exit 1
    else
        print_error ".env.example not found"
        exit 1
    fi
fi

# Load environment
source .env
print_success "Environment loaded"

# Check API key
case $LLM_PROVIDER in
    deepseek)
        if [ -z "$DEEPSEEK_API_KEY" ] || [ "$DEEPSEEK_API_KEY" = "your-deepseek-api-key-here" ]; then
            print_error "Please set DEEPSEEK_API_KEY in .env"
            exit 1
        fi
        ;;
    qwen)
        if [ -z "$QWEN_API_KEY" ] || [ "$QWEN_API_KEY" = "your-qwen-api-key-here" ]; then
            print_error "Please set QWEN_API_KEY in .env"
            exit 1
        fi
        ;;
    openai)
        if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
            print_error "Please set OPENAI_API_KEY in .env"
            exit 1
        fi
        ;;
esac

# Check dependencies
echo ""
echo "Checking dependencies..."
if ! python3 -c "import langgraph" &> /dev/null; then
    print_warning "Dependencies not installed"
    echo "Installing dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_success "Dependencies already installed"
fi

# Setup database
echo ""
echo "Checking database..."
if [ ! -f data/chinook.db ]; then
    echo "Setting up database..."
    python3 scripts/setup_db.py
    print_success "Database setup complete"
else
    print_success "Database exists"
fi

# Create logs directory
mkdir -p logs

# Start server
echo ""
echo "=========================================="
echo "Starting Development Server..."
echo "=========================================="
echo ""

python3 -m uvicorn apps.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
