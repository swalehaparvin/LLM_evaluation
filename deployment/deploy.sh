#!/bin/bash

# SafeGuardLLM Docker Deployment Script
# This script automates the deployment process for SafeGuardLLM using Docker

set -e  # Exit on any error

echo "🚀 SafeGuardLLM Docker Deployment Script"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env_file() {
    print_status "Checking environment configuration..."
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        print_status "Copying .env.example to .env..."
        cp .env.example .env
        print_warning "Please edit .env file with your API keys before continuing"
        print_warning "Required: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY"
        read -p "Press Enter after updating .env file..."
    fi
    print_success "Environment file found"
}

# Validate required environment variables
validate_env() {
    print_status "Validating environment variables..."
    source .env
    
    REQUIRED_VARS=("OPENAI_API_KEY" "ANTHROPIC_API_KEY" "GOOGLE_API_KEY")
    MISSING_VARS=()
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ] || [ "${!var}" = "your-key-here" ] || [[ "${!var}" == *"your-"* ]]; then
            MISSING_VARS+=("$var")
        fi
    done
    
    if [ ${#MISSING_VARS[@]} -ne 0 ]; then
        print_error "Missing or invalid environment variables:"
        for var in "${MISSING_VARS[@]}"; do
            echo "  - $var"
        done
        print_error "Please update your .env file with valid API keys"
        exit 1
    fi
    
    print_success "Environment variables validated"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop any existing containers
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans
    
    # Build images
    print_status "Building application image..."
    docker-compose build app
    
    # Start services
    print_status "Starting all services..."
    docker-compose up -d
    
    print_success "Services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for PostgreSQL database..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T postgres pg_isready -U safeguard_user -d safeguard_llm > /dev/null 2>&1; then
            break
        fi
        sleep 2
        ((timeout-=2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Database failed to start within 60 seconds"
        docker-compose logs postgres
        exit 1
    fi
    
    # Wait for application
    print_status "Waiting for application to be ready..."
    timeout=120
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:5000/api/stats > /dev/null 2>&1; then
            break
        fi
        sleep 3
        ((timeout-=3))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Application failed to start within 120 seconds"
        docker-compose logs app
        exit 1
    fi
    
    print_success "All services are ready"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    docker-compose exec app npm run db:push
    print_success "Database migrations completed"
}

# Display deployment status
show_status() {
    echo ""
    print_success "SafeGuardLLM deployed successfully!"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Web Interface: http://localhost:80"
    echo "   Direct App:    http://localhost:5000"
    echo "   Database:      localhost:5432"
    echo "   Redis Cache:   localhost:6379"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "📝 Useful Commands:"
    echo "   View logs:           docker-compose logs -f [service]"
    echo "   Stop services:       docker-compose down"
    echo "   Restart service:     docker-compose restart [service]"
    echo "   Database shell:      docker-compose exec postgres psql -U safeguard_user -d safeguard_llm"
    echo "   Application shell:   docker-compose exec app bash"
    echo ""
}

# Cleanup function
cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Deployment failed!"
        print_status "Showing service logs for debugging..."
        docker-compose logs --tail=50
        echo ""
        print_status "To clean up failed deployment:"
        echo "  docker-compose down --remove-orphans"
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main deployment flow
main() {
    echo ""
    check_docker
    check_env_file
    validate_env
    echo ""
    
    read -p "🚀 Ready to deploy SafeGuardLLM? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled"
        exit 0
    fi
    
    echo ""
    deploy_services
    wait_for_services
    run_migrations
    show_status
}

# Parse command line arguments
case "${1:-}" in
    "dev")
        print_status "Starting development deployment..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        ;;
    "stop")
        print_status "Stopping SafeGuardLLM services..."
        docker-compose down
        print_success "Services stopped"
        ;;
    "logs")
        docker-compose logs -f "${2:-}"
        ;;
    "status")
        docker-compose ps
        ;;
    "clean")
        print_warning "This will remove all containers and volumes (DATA WILL BE LOST)"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v --remove-orphans
            docker system prune -f
            print_success "Cleanup completed"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Deploy SafeGuardLLM in production mode"
        echo "  dev        Deploy in development mode"
        echo "  stop       Stop all services"
        echo "  logs       View logs (optionally specify service)"
        echo "  status     Show service status"
        echo "  clean      Remove all containers and data"
        echo "  help       Show this help message"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac