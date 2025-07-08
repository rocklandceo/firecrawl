#!/bin/bash
# Development convenience script for Firecrawl-Streamlit Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_status ".env file created. Please add your FIRECRAWL_API_KEY."
        else
            print_error ".env.example not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Main command handling
case "$1" in
    "start"|"up")
        print_status "Starting Firecrawl-Streamlit development environment..."
        check_docker
        check_env
        docker-compose up --build
        ;;
    
    "stop"|"down")
        print_status "Stopping Firecrawl-Streamlit development environment..."
        docker-compose down
        ;;
    
    "restart")
        print_status "Restarting Firecrawl-Streamlit development environment..."
        check_docker
        docker-compose restart
        ;;
    
    "rebuild")
        print_status "Rebuilding Firecrawl-Streamlit containers..."
        check_docker
        docker-compose down
        docker-compose build --no-cache
        docker-compose up
        ;;
    
    "logs")
        print_status "Showing application logs..."
        docker-compose logs -f firecrawl-app
        ;;
    
    "shell")
        print_status "Opening shell in development container..."
        docker-compose exec firecrawl-app /bin/bash
        ;;
    
    "test")
        print_status "Running tests in container..."
        docker-compose exec firecrawl-app python -m pytest tests/ -v
        ;;
    
    "install"|"deps")
        print_status "Installing/updating dependencies..."
        docker-compose exec firecrawl-app pip install -r requirements.txt
        ;;
    
    "clean")
        print_status "Cleaning up Docker resources..."
        docker-compose down --volumes --remove-orphans
        docker system prune -f
        ;;
    
    "status")
        print_status "Checking container status..."
        docker-compose ps
        ;;
    
    "prod")
        print_status "Starting production environment..."
        check_docker
        check_env
        docker-compose -f docker-compose.prod.yml up --build -d
        ;;
    
    "prod-stop")
        print_status "Stopping production environment..."
        docker-compose -f docker-compose.prod.yml down
        ;;
    
    "backup")
        print_status "Creating data backup..."
        timestamp=$(date +"%Y%m%d_%H%M%S")
        docker run --rm -v "$(pwd)/data:/data" -v "$(pwd)/backups:/backup" alpine tar czf "/backup/data_backup_${timestamp}.tar.gz" -C /data .
        print_status "Backup created: backups/data_backup_${timestamp}.tar.gz"
        ;;
    
    "help"|"")
        echo -e "${BLUE}Firecrawl-Streamlit Development Helper${NC}"
        echo ""
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start, up       Start development environment"
        echo "  stop, down      Stop development environment"
        echo "  restart         Restart the application"
        echo "  rebuild         Rebuild containers and start"
        echo "  logs            Show application logs"
        echo "  shell           Open shell in container"
        echo "  test            Run tests"
        echo "  install, deps   Install/update dependencies"
        echo "  clean           Clean up Docker resources"
        echo "  status          Check container status"
        echo "  prod            Start production environment"
        echo "  prod-stop       Stop production environment"
        echo "  backup          Create data backup"
        echo "  help            Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./dev.sh start          # Start development server"
        echo "  ./dev.sh logs           # View logs"
        echo "  ./dev.sh shell          # Access container shell"
        echo "  ./dev.sh test           # Run tests"
        ;;
    
    *)
        print_error "Unknown command: $1"
        print_status "Run './dev.sh help' for available commands"
        exit 1
        ;;
esac
