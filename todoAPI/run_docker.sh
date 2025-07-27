#!/bin/bash

# Script to manage the Docker container for the Todo API

# Exit immediately if a command exits with a non-zero status.
set -e

# Define variables
IMAGE_NAME="todo-api"
CONTAINER_NAME="todo-api-container"

# Function to display usage
usage() {
  echo "Usage: $0 {build|start|stop|logs|restart}"
  exit 1
}

# Build the Docker image
build() {
  echo "Building Docker image: $IMAGE_NAME..."
  docker build -t $IMAGE_NAME .
  echo "Build complete."
}

# Start the Docker container
start() {
  echo "Starting Docker container: $CONTAINER_NAME..."
  # Stop and remove existing container if it exists
  if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    docker stop $CONTAINER_NAME
  fi
  if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
    docker rm $CONTAINER_NAME
  fi
  # Run the container
  docker run -d -p 5001:5001 --name $CONTAINER_NAME $IMAGE_NAME
  echo "Container started."
}

# Stop the Docker container
stop() {
  echo "Stopping Docker container: $CONTAINER_NAME..."
  if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    echo "Container stopped and removed."
  else
    echo "Container is not running."
  fi
}

# View container logs
logs() {
  echo "Showing logs for container: $CONTAINER_NAME..."
  docker logs -f $CONTAINER_NAME
}

# Restart the container
restart() {
  stop
  start
}

# Main logic
case "$1" in
  build)
    build
    ;;
  start)
    start
    ;;
  stop)
    stop
    ;;
  logs)
    logs
    ;;
  restart)
    restart
    ;;
  *)
    usage
    ;;
esac
