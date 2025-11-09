#!/bin/bash

# RouterDown Quick Start Script
# This script helps you get RouterDown up and running quickly on your Raspberry Pi

set -e  # Exit on error

echo "======================================"
echo "  RouterDown Quick Start"
echo "======================================"
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo "  sudo usermod -aG docker $USER"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed!"
    echo "Please install docker-compose first:"
    echo "  sudo apt-get install docker-compose"
    exit 1
fi

# Change to the docker directory
cd "$(dirname "$0")"

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created!"
        echo ""
        echo "⚠️  IMPORTANT: Please edit the .env file with your Home Assistant details:"
        echo "   - HA_HOST: Your Home Assistant IP address"
        echo "   - HA_WEBHOOK_ID: Your webhook ID"
        echo ""
        read -p "Press Enter to edit .env file now, or Ctrl+C to exit and edit later..."
        ${EDITOR:-nano} .env
    else
        echo "❌ .env.example not found!"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Create logs directory if it doesn't exist (in parent directory)
if [ ! -d ../logs ]; then
    echo "📁 Creating logs directory..."
    mkdir -p ../logs
    echo "✅ logs directory created!"
fi

# Build and start the container
echo ""
echo "🔨 Building and starting RouterDown container..."
docker-compose up -d --build

echo ""
echo "✅ RouterDown is now running!"
echo ""
echo "Useful commands (run from docker/ directory):"
echo "  docker-compose logs -f          # View real-time logs"
echo "  docker-compose restart          # Restart the service"
echo "  docker-compose down             # Stop the service"
echo "  cat ../logs/networkinfo.log     # View log file"
echo ""
echo "Logs are saved to: $(cd .. && pwd)/logs/networkinfo.log"
echo ""
