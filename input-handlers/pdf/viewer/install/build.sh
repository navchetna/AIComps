#!/bin/bash

# Docker Build Script for doc-flow
# This script helps build Docker images with the correct environment variables

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Doc-Flow Docker Build Script ===${NC}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your configuration before building.${NC}"
    exit 1
fi

# Source the .env file
source .env

# Display current configuration
echo -e "${GREEN}Current Configuration:${NC}"
echo "NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:5001}"
echo "FRONTEND_URL: ${FRONTEND_URL:-http://localhost:3000}"
echo ""

read -p "Do you want to proceed with these settings? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Build cancelled. Please update .env file and try again."
    exit 1
fi

# Check if proxy is needed
USE_PROXY=""
if [ ! -z "$http_proxy" ] || [ ! -z "$https_proxy" ]; then
    echo -e "${YELLOW}Proxy detected. Will use proxy settings.${NC}"
    USE_PROXY="--build-arg no_proxy=$no_proxy --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy"
fi

echo -e "\n${GREEN}Building images...${NC}\n"

# Resolve directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"
FRONTEND_DIR="${SCRIPT_DIR}/../frontend"

# Image tags (must match docker-compose.yaml)
BACKEND_IMAGE="navchetna/doc-flow-backend:latest"
FRONTEND_IMAGE="navchetna/doc-flow-frontend:latest"

echo "Building backend image: ${BACKEND_IMAGE}"
sudo docker build \
    -t "${BACKEND_IMAGE}" \
    ${USE_PROXY} \
    -f "${BACKEND_DIR}/Dockerfile" \
    "${BACKEND_DIR}"

echo "Building frontend image: ${FRONTEND_IMAGE}"
sudo docker build \
    -t "${FRONTEND_IMAGE}" \
    ${USE_PROXY} \
    -f "${FRONTEND_DIR}/Dockerfile" \
    "${FRONTEND_DIR}"

echo -e "\n${GREEN}Build completed successfully!${NC}"
echo -e "\nTo start the services, run:"
echo -e "  ${YELLOW}docker compose up -d${NC}"
echo -e "\nTo view logs, run:"
echo -e "  ${YELLOW}docker compose logs -f${NC}"
