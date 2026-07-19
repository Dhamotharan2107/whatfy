#!/bin/bash
set -e

# Whatfy Docker Build and Push Script
# Repository: tertwer/whatfy

REPO_NAME="tertwer/whatfy"
VERSION=${1:-"latest"}
DOCKERFILE="Dockerfile"

echo "========================================"
echo "Whatfy Docker Build and Push Script"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    exit 1
fi

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username: tertwer"; then
    echo "⚠️  Not logged in to Docker Hub"
    echo "Login required:"
    docker login
fi

# Build arguments
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VERSION=${VERSION:-"latest"}
LATEST_TAG="latest"
VARIANT_TAG="${VERSION}"

echo "Building Docker image: ${REPO_NAME}"
echo "Version: ${VERSION}"
echo "Date: ${BUILD_DATE}"
echo ""

# Build the Docker image
echo "Step 1: Building Docker image..."
docker build \
    --build-arg BUILD_DATE="${BUILD_DATE}" \
    --build-arg VERSION="${VERSION}" \
    -t ${REPO_NAME}:${LATEST_TAG} \
    -t ${REPO_NAME}:${VARIANT_TAG} \
    -f ${DOCKERFILE} \
    .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker build successful"
echo ""

# Show image info
echo "Image size:"
docker images ${REPO_NAME}
echo ""

# Push to Docker Hub
echo "Step 2: Pushing to Docker Hub..."
echo "Pushing ${REPO_NAME}:${LATEST_TAG}"
docker push ${REPO_NAME}:${LATEST_TAG}

if [ $? -ne 0 ]; then
    echo "❌ Failed to push ${REPO_NAME}:${LATEST_TAG}"
    exit 1
fi

echo "Pushing ${REPO_NAME}:${VARIANT_TAG}"
docker push ${REPO_NAME}:${VARIANT_TAG}

if [ $? -ne 0 ]; then
    echo "❌ Failed to push ${REPO_NAME}:${VARIANT_TAG}"
    exit 1
fi

echo ""
echo "✅ Docker push successful"
echo ""
echo "========================================"
echo "Docker Image Details"
echo "========================================"
echo "Repository: ${REPO_NAME}"
echo "Tags: ${LATEST_TAG}, ${VARIANT_TAG}"
echo "Image Size:"
docker images ${REPO_NAME} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
echo ""

echo "========================================"
echo "To use this image:"
echo "========================================"
echo "Docker pull:"
echo "  docker pull ${REPO_NAME}:${LATEST_TAG}"
echo "  docker pull ${REPO_NAME}:${VARIANT_TAG}"
echo ""
echo "Docker Compose:"
echo "  docker compose up -d"
echo ""
echo "Run directly:"
echo "  docker run -d -p 5000:5000 -v whatsmeow_data:/app/whatsmeow_server ${REPO_NAME}:${LATEST_TAG}"
echo ""
echo "========================================"
echo "Build complete!"
echo "========================================"