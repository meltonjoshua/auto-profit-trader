#!/bin/bash

# Auto Profit Trader - Docker Deployment Script
# This script helps deploy the trading bot in a Docker container

set -e

echo "🐳 Auto Profit Trader Docker Deployment"
echo "======================================="

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
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data config

# Check if config.json exists
if [ ! -f "config.json" ]; then
    print_warning "config.json not found. You'll need to configure the bot before starting."
    print_status "Run 'python production_setup.py' to create configuration."
fi

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    docker-compose build
    print_success "Docker image built successfully!"
}

# Function to start the container
start_container() {
    print_status "Starting Auto Profit Trader container..."
    docker-compose up -d
    print_success "Container started successfully!"
    
    print_status "Container status:"
    docker-compose ps
    
    print_status "To view logs, run: docker-compose logs -f"
    print_status "To stop the container, run: docker-compose down"
}

# Function to show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose logs -f
}

# Function to stop the container
stop_container() {
    print_status "Stopping Auto Profit Trader container..."
    docker-compose down
    print_success "Container stopped successfully!"
}

# Function to restart the container
restart_container() {
    print_status "Restarting Auto Profit Trader container..."
    docker-compose restart
    print_success "Container restarted successfully!"
}

# Function to show container status
show_status() {
    print_status "Container status:"
    docker-compose ps
    
    print_status "Resource usage:"
    docker stats --no-stream auto-profit-trader
}

# Function to enter container shell
enter_shell() {
    print_status "Entering container shell..."
    docker-compose exec auto-profit-trader bash
}

# Function to update and restart
update_and_restart() {
    print_status "Updating and restarting container..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    print_success "Container updated and restarted!"
}

# Main menu
case "$1" in
    "build")
        build_image
        ;;
    "start")
        start_container
        ;;
    "stop")
        stop_container
        ;;
    "restart")
        restart_container
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "shell")
        enter_shell
        ;;
    "update")
        update_and_restart
        ;;
    "deploy")
        build_image
        start_container
        ;;
    *)
        echo "Usage: $0 {build|start|stop|restart|logs|status|shell|update|deploy}"
        echo ""
        echo "Commands:"
        echo "  build    - Build the Docker image"
        echo "  start    - Start the container"
        echo "  stop     - Stop the container"
        echo "  restart  - Restart the container"
        echo "  logs     - Show container logs"
        echo "  status   - Show container status and resource usage"
        echo "  shell    - Enter container shell"
        echo "  update   - Rebuild and restart container"
        echo "  deploy   - Build and start (full deployment)"
        echo ""
        echo "Examples:"
        echo "  $0 deploy    # Full deployment"
        echo "  $0 logs      # Monitor logs"
        echo "  $0 status    # Check status"
        exit 1
        ;;
esac
