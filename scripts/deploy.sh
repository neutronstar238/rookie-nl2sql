#!/bin/bash
# NL2SQL Deployment Script
# M13: One-click deployment

set -e

echo "=========================================="
echo "NL2SQL System Deployment"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found"
    if [ -f .env.example ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env and add your API keys before continuing"
        echo "Required: DEEPSEEK_API_KEY or QWEN_API_KEY or OPENAI_API_KEY"
        exit 1
    else
        print_error ".env.example not found"
        exit 1
    fi
fi

# Validate required environment variables
echo ""
echo "Validating environment configuration..."
source .env

if [ -z "$LLM_PROVIDER" ]; then
    print_error "LLM_PROVIDER not set in .env"
    exit 1
fi

case $LLM_PROVIDER in
    deepseek)
        if [ -z "$DEEPSEEK_API_KEY" ]; then
            print_error "DEEPSEEK_API_KEY not set in .env"
            exit 1
        fi
        print_success "Using DeepSeek provider"
        ;;
    qwen)
        if [ -z "$QWEN_API_KEY" ]; then
            print_error "QWEN_API_KEY not set in .env"
            exit 1
        fi
        print_success "Using Qwen provider"
        ;;
    openai)
        if [ -z "$OPENAI_API_KEY" ]; then
            print_error "OPENAI_API_KEY not set in .env"
            exit 1
        fi
        print_success "Using OpenAI provider"
        ;;
    *)
        print_error "Unknown LLM_PROVIDER: $LLM_PROVIDER"
        exit 1
        ;;
esac

# Check if Docker is installed
echo ""
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Setup database
echo ""
echo "Setting up database..."
if [ ! -f data/chinook.db ]; then
    echo "Downloading Chinook database..."
    python3 scripts/setup_db.py
    print_success "Database downloaded"
else
    print_success "Database already exists"
fi

# Build Docker image
echo ""
echo "Building Docker image..."
if docker-compose build; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Start services
echo ""
echo "Starting services..."
if docker-compose up -d; then
    print_success "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait for service to be ready
echo ""
echo "Waiting for service to be ready..."
sleep 5

max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Service is healthy!"
        break
    fi
    attempt=$((attempt + 1))
    echo "Waiting... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    print_error "Service failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Display service info
echo ""
echo "=========================================="
echo "Deployment Successful!"
echo "=========================================="
echo ""
echo "Service URL: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose stop"
echo "  Restart services: docker-compose restart"
echo "  Remove services:  docker-compose down"
echo ""
print_success "Ready to accept queries!"
