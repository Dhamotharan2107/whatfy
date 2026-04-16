#!/bin/bash
set -e

IMAGE="tertwer/whatfy"

echo "===> Building Docker image: $IMAGE"
docker build -t "$IMAGE" .

echo "===> Pushing to Docker Hub: $IMAGE"
docker push "$IMAGE"

echo "===> Done! Image pushed: $IMAGE"
