#!/bin/bash
set -e

echo "=========================================="
echo "  Plane VPS Setup Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# Install Docker if not present
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable docker
  systemctl start docker
fi

# Install Docker Compose v2 if not present
if ! docker compose version &> /dev/null; then
  echo "Installing Docker Compose..."
  apt-get update
  apt-get install -y docker-compose-plugin
fi

# Create deployment directory
DEPLOY_DIR="$HOME/plane-deploy"
mkdir -p "$DEPLOY_DIR/apps/api"

echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy deploy/vps/ contents to your VPS: $DEPLOY_DIR"
echo "2. Edit $DEPLOY_DIR/.env with your settings"
echo "3. Edit $DEPLOY_DIR/apps/api/.env with your settings"
echo "4. Add your SSH key to GitHub secrets"
echo "5. Push to main branch to trigger deployment"
echo ""
