# Docker Quick Start Guide

## Prerequisites
- Docker installed on your system
- Docker Compose installed

## Quick Deployment

### 1. Clone and Setup
```bash
git clone https://github.com/meltonjoshua/auto-profit-trader.git
cd auto-profit-trader
```

### 2. Configure Trading Bot
```bash
# Set up your trading configuration
python production_setup.py
```

### 3. Deploy with Docker
```bash
# Build and start the container
./docker-deploy.sh deploy
```

### 4. Monitor the Bot
```bash
# View real-time logs
./docker-deploy.sh logs

# Check container status
./docker-deploy.sh status

# Enter container for debugging
./docker-deploy.sh shell
```

## Container Management

### Available Commands
- `./docker-deploy.sh build` - Build the Docker image
- `./docker-deploy.sh start` - Start the container
- `./docker-deploy.sh stop` - Stop the container
- `./docker-deploy.sh restart` - Restart the container
- `./docker-deploy.sh logs` - View logs
- `./docker-deploy.sh status` - Check status and resource usage
- `./docker-deploy.sh shell` - Enter container shell
- `./docker-deploy.sh update` - Update and restart
- `./docker-deploy.sh deploy` - Full deployment (build + start)

### Container Features
- **Auto-restart**: Automatically restarts on failure
- **Persistent Storage**: Logs and data persist across restarts
- **Resource Limits**: CPU and memory limits for stability
- **Health Monitoring**: Built-in health checks
- **Security**: Runs as non-root user

## Troubleshooting

### Check Container Status
```bash
docker ps
docker logs auto-profit-trader
```

### Enter Container for Debugging
```bash
./docker-deploy.sh shell
```

### View Resource Usage
```bash
docker stats auto-profit-trader
```

### Restart Container
```bash
./docker-deploy.sh restart
```

## Configuration Files

The following files will be mounted as volumes:
- `./config/` - Trading configuration
- `./logs/` - Application logs
- `./data/` - Database and data files

## Security Notes

- Container runs as non-root user (trader:1000)
- API keys are encrypted and stored securely
- Resource limits prevent excessive usage
- Network isolation through Docker networks
