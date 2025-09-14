#!/bin/bash

# Banking Voice App Docker Manager
set -e

case "$1" in
  "start")
    echo "Starting Banking Voice App services..."

    # Start MongoDB
    echo "1. Starting MongoDB..."
    docker-compose up -d mongodb

    # Wait for MongoDB to be healthy
    echo "2. Waiting for MongoDB to be ready..."
    while ! docker-compose exec mongodb mongosh --eval "db.runCommand('ping')" >/dev/null 2>&1; do
      echo "   Waiting for MongoDB..."
      sleep 2
    done
    echo "   MongoDB is ready!"

    # Build and start the app
    echo "3. Building and starting the application..."
    docker build -t banking-voice-app .

    # Stop existing app container if running
    docker stop banking-app 2>/dev/null || true
    docker rm banking-app 2>/dev/null || true

    # Start the application container
    docker run -d \
      --name banking-app \
      --network banking-voice-app_banking_network \
      -p 8000:8000 \
      -e MONGODB_URL="mongodb://admin:password123@banking_voice_mongodb:27017/banking_voice_app?authSource=admin" \
      -e DATABASE_NAME="banking_voice_app" \
      -e API_HOST="0.0.0.0" \
      -e API_PORT="8000" \
      -e DEBUG="false" \
      banking-voice-app

    echo "4. Services started successfully!"
    echo ""
    echo "🚀 Banking Voice App is running at: http://localhost:8000"
    echo "🤖 N8N Workflow Editor: http://localhost:5678"
    echo "📊 App Health check: http://localhost:8000/health"
    echo "📊 N8N Health check: http://localhost:5678/healthz"
    echo ""
    echo "🔧 Setup N8N Workflow: Follow instructions in setup-n8n-workflow.md"
    echo "To view app logs: docker logs banking_voice_app"
    echo "To view N8N logs: docker logs banking_voice_n8n"
    echo "To stop services: ./docker-run.sh stop"
    ;;

  "stop")
    echo "Stopping Banking Voice App services..."
    docker stop banking-app 2>/dev/null || true
    docker rm banking-app 2>/dev/null || true
    docker-compose down
    echo "✅ All services stopped."
    ;;

  "logs")
    echo "Application logs:"
    docker logs -f banking-app
    ;;

  "status")
    echo "Service Status:"
    echo "📊 MongoDB:"
    docker-compose ps mongodb
    echo ""
    echo "🏦 Banking App:"
    docker ps --filter name=banking-app --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    ;;

  "health")
    echo "Health Check:"
    if curl -s http://localhost:8000/health >/dev/null; then
      echo "✅ Application is healthy"
      curl -s http://localhost:8000/health | jq .
    else
      echo "❌ Application is not responding"
    fi
    ;;

  *)
    echo "Banking Voice App Docker Manager"
    echo ""
    echo "Usage: $0 {start|stop|logs|status|health}"
    echo ""
    echo "Commands:"
    echo "  start   - Start all services (MongoDB + Banking App)"
    echo "  stop    - Stop all services"
    echo "  logs    - Show application logs"
    echo "  status  - Show service status"
    echo "  health  - Check application health"
    echo ""
    exit 1
    ;;
esac