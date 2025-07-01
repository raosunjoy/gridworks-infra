#!/bin/bash

# GridWorks Infra - Development Environment Setup Script
# This script sets up the complete development environment for B2B infrastructure

echo "🚀 GridWorks Infra - Setting up B2B Infrastructure Development Environment"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    print_error "Please run this script from the GridWorks-Infra root directory"
    exit 1
fi

# Create necessary directories for B2B infrastructure
print_status "Creating B2B infrastructure directories..."

mkdir -p shared-infrastructure/b2b-services/{anonymous-services,ai-suite,trading-as-service,banking-as-service}
mkdir -p shared-infrastructure/b2b-services/anonymous-services/{zk-proofs,butler-ai,identity-management}
mkdir -p shared-infrastructure/b2b-services/ai-suite/{support-engine,intelligence-engine,moderator-engine}
mkdir -p shared-infrastructure/b2b-services/trading-as-service/{order-management,risk-engine,market-data}
mkdir -p shared-infrastructure/b2b-services/banking-as-service/{accounts,payments,compliance}
mkdir -p infrastructure/monitoring/{prometheus,grafana,elasticsearch}
mkdir -p infrastructure/security/{vault,certificates,policies}

print_success "Directory structure created"

# Create Python virtual environment
print_status "Setting up Python virtual environment..."

if command -v python3 &> /dev/null; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    print_success "Python virtual environment created"
else
    print_error "Python 3 is not installed. Please install Python 3.9 or later"
    exit 1
fi

# Install Python dependencies
print_status "Installing Python dependencies..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_warning "requirements.txt not found. Skipping Python dependencies"
fi

# Check Node.js installation
print_status "Checking Node.js installation..."

if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    print_success "Node.js $NODE_VERSION is installed"
else
    print_error "Node.js is not installed. Please install Node.js 18 or later"
    exit 1
fi

# Install dependencies for Partners Portal
print_status "Installing Partners Portal dependencies..."

cd business-entity-1-partners-portal/partner-portal
if [ -f "package.json" ]; then
    npm install
    print_success "Partners Portal dependencies installed"
else
    print_warning "package.json not found in Partners Portal"
fi
cd ../..

# Create environment files
print_status "Creating environment configuration files..."

# Main .env file
cat > .env.development << 'EOF'
# GridWorks Infra - B2B Infrastructure Environment Configuration

# Application
NODE_ENV=development
APP_NAME=GridWorks-Infra
APP_VERSION=1.0.0
API_URL=http://localhost:8000

# Database
DATABASE_URL=postgresql://gridworks:gridworks@localhost:5432/gridworks_infra
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your-development-jwt-secret-change-in-production
ENCRYPTION_KEY=your-development-encryption-key-change-in-production

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Trading Services
ZERODHA_API_KEY=your-zerodha-api-key
ZERODHA_API_SECRET=your-zerodha-api-secret
UPSTOX_API_KEY=your-upstox-api-key
UPSTOX_API_SECRET=your-upstox-api-secret

# WhatsApp Business
WHATSAPP_API_KEY=your-whatsapp-api-key
WHATSAPP_PHONE_NUMBER=your-whatsapp-number

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Development Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
PARTNERS_PORTAL_PORT=3001
EOF

print_success "Environment configuration created"

# Create Docker Compose for local development
print_status "Creating Docker Compose configuration..."

cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: gridworks-postgres
    environment:
      POSTGRES_USER: gridworks
      POSTGRES_PASSWORD: gridworks
      POSTGRES_DB: gridworks_infra
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: gridworks-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    container_name: gridworks-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./infrastructure/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    container_name: gridworks-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
EOF

print_success "Docker Compose configuration created"

# Create Makefile for common tasks
print_status "Creating Makefile for development tasks..."

cat > Makefile << 'EOF'
# GridWorks Infra - Development Makefile

.PHONY: help setup dev test build deploy clean

help:
	@echo "GridWorks Infra - B2B Infrastructure Development Commands"
	@echo ""
	@echo "make setup     - Set up development environment"
	@echo "make dev       - Start development servers"
	@echo "make test      - Run all tests"
	@echo "make build     - Build production artifacts"
	@echo "make deploy    - Deploy to staging/production"
	@echo "make clean     - Clean build artifacts"

setup:
	@echo "Setting up development environment..."
	@bash setup-development.sh

dev:
	@echo "Starting development servers..."
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "Starting backend server..."
	@cd shared-infrastructure/core-platform && uvicorn main:app --reload --port 8000 &
	@echo "Starting Partners Portal..."
	@cd business-entity-1-partners-portal/partner-portal && npm run dev &

test:
	@echo "Running tests..."
	@pytest shared-infrastructure/core-platform/tests -v
	@cd business-entity-1-partners-portal/partner-portal && npm test

build:
	@echo "Building production artifacts..."
	@docker build -t gridworks-infra-backend:latest .
	@cd business-entity-1-partners-portal/partner-portal && npm run build

deploy:
	@echo "Deploying to production..."
	@echo "TODO: Add deployment commands"

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".next" -exec rm -rf {} +
	@find . -type d -name "node_modules" -exec rm -rf {} +
	@find . -type d -name "dist" -exec rm -rf {} +
EOF

print_success "Makefile created"

# Create VS Code workspace settings
print_status "Creating VS Code workspace settings..."

mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.python"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
EOF

print_success "VS Code settings created"

# Final setup message
echo ""
print_success "🎉 Development environment setup complete!"
echo ""
print_status "Next steps:"
echo "  1. Copy .env.development to .env and update with your API keys"
echo "  2. Run 'docker-compose -f docker-compose.dev.yml up' to start databases"
echo "  3. Run 'make dev' to start development servers"
echo "  4. Visit http://localhost:3001 for Partners Portal"
echo "  5. Visit http://localhost:8000/docs for API documentation"
echo ""
print_status "For help, run: make help"