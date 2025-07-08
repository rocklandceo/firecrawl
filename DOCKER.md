# Docker Development Guide
## Firecrawl-Streamlit Web Scraper

This project is fully containerized with Docker for consistent development, testing, and deployment environments.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git (for cloning)

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd firecrawl

# Copy environment template
cp .env.example .env

# Add your Firecrawl API key to .env
echo "FIRECRAWL_API_KEY=your_actual_api_key_here" >> .env

# Start development environment
./dev.sh start
```

The application will be available at: **http://localhost:8501**

## 🛠️ Development Commands

The `dev.sh` script provides convenient commands for Docker development:

### Essential Commands
```bash
./dev.sh start      # Start development environment
./dev.sh stop       # Stop development environment  
./dev.sh logs       # View application logs
./dev.sh shell      # Access container shell
./dev.sh restart    # Restart the application
```

### Advanced Commands
```bash
./dev.sh rebuild    # Rebuild containers from scratch
./dev.sh test       # Run tests in container
./dev.sh clean      # Clean up Docker resources
./dev.sh status     # Check container status
./dev.sh backup     # Create data backup
```

### Production Commands
```bash
./dev.sh prod       # Start production environment
./dev.sh prod-stop  # Stop production environment
```

## 📁 Project Structure

```
firecrawl/
├── streamlit-app/          # Application source code
├── config/                 # Configuration files  
├── data/                   # Persistent data (mounted volume)
├── logs/                   # Application logs (mounted volume)
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
├── dev.sh                  # Development helper script
└── .env                    # Environment variables
```

## 🔧 Development Workflow

### 1. Live Development
- Source code is mounted as a volume for live reloading
- Changes to Python files trigger automatic Streamlit reloads
- No need to rebuild containers for code changes

### 2. Dependencies
```bash
# Add new dependency to requirements.txt, then:
./dev.sh install

# Or rebuild if needed:
./dev.sh rebuild
```

### 3. Debugging
```bash
# View logs
./dev.sh logs

# Access container shell
./dev.sh shell

# Inside container, you can:
python -c "import streamlit; print(streamlit.__version__)"
pip list
pytest tests/ -v
```

### 4. Testing
```bash
# Run all tests
./dev.sh test

# Run specific test file
./dev.sh shell
pytest tests/test_firecrawl_client.py -v
```

## 🏗️ Container Architecture

### Development Container
- **Base Image**: `python:3.11-slim`
- **Virtual Environment**: `/opt/venv` (isolated dependencies)
- **User**: `appuser` (non-root for security)
- **Ports**: `8501` (Streamlit)
- **Volumes**: Source code, data, logs mounted

### Production Container
- **Optimized**: Smaller image, no dev dependencies
- **Security**: Read-only filesystem, resource limits
- **Health Checks**: Automatic container health monitoring
- **Logging**: Structured logging with rotation

## 🔒 Security Features

### Container Security
- Non-root user execution
- Read-only filesystem (production)
- No new privileges
- Resource limits (CPU/memory)
- Health checks for monitoring

### Data Security
- Environment variables for sensitive data
- Separated volumes for data persistence
- No secrets in Docker images
- .dockerignore excludes sensitive files

## 🌍 Environment Configuration

### Required Environment Variables
```bash
FIRECRAWL_API_KEY=fc-your-api-key-here  # Required for web scraping
```

### Optional Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-...             # For AI processing
ENVIRONMENT=development                   # development/production
STREAMLIT_SERVER_HEADLESS=true          # Run without browser
```

## 📊 Data Management

### Persistent Data
- **Location**: `./data/` (host) → `/app/data/` (container)
- **Contents**: Scraped content, processed data, metadata
- **Backups**: Use `./dev.sh backup` for automated backups

### Data Structure
```
data/
├── scraped_content/        # Raw scraped data (domain-organized)
├── processed_content/      # AI-optimized content
├── metadata/              # File metadata and indexes
├── exports/               # Generated export files
├── backups/               # Automatic backups
└── temp/                  # Temporary processing files
```

## 🚢 Production Deployment

### Production Mode
```bash
# Start production environment
./dev.sh prod

# Features:
# - Optimized container (smaller size)
# - Enhanced security settings
# - Resource limits
# - Structured logging
# - Health monitoring
```

### Production Considerations
- Set up reverse proxy (Nginx configuration included)
- Configure SSL certificates
- Set up monitoring and alerting
- Regular backup strategy
- Log aggregation

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Stop any existing containers
./dev.sh stop
docker ps -a

# Or use different port in docker-compose.yml
ports:
  - "8502:8501"  # Use port 8502 instead
```

#### Container Won't Start
```bash
# Check logs
./dev.sh logs

# Rebuild from scratch
./dev.sh clean
./dev.sh rebuild
```

#### Permission Issues
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/
```

#### API Key Issues
```bash
# Verify environment file
cat .env | grep FIRECRAWL_API_KEY

# Test API key in container
./dev.sh shell
python -c "import os; print('API Key:', os.getenv('FIRECRAWL_API_KEY'))"
```

## 💡 Tips & Best Practices

### Development Tips
1. **Use the dev.sh script** - It handles common tasks automatically
2. **Monitor logs** - Use `./dev.sh logs` to track application behavior
3. **Regular backups** - Run `./dev.sh backup` before major changes
4. **Clean resources** - Use `./dev.sh clean` to free disk space

### Performance Tips
1. **Volume mounts** - Only essential directories are mounted
2. **Layer caching** - Dependencies installed in separate layer
3. **Multi-stage builds** - Separate dev/prod optimizations
4. **Health checks** - Automatic container restart on failures

### Security Tips
1. **Never commit .env** - Use .env.example as template
2. **Regular updates** - Keep base images and dependencies updated
3. **Non-root execution** - All processes run as appuser
4. **Resource limits** - Production containers have CPU/memory limits

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Streamlit Deployment Guide](https://docs.streamlit.io/knowledge-base/tutorials/deploy)
- [Firecrawl API Documentation](https://docs.firecrawl.dev/)

---

**Need Help?** Run `./dev.sh help` for available commands or check the logs with `./dev.sh logs`.
