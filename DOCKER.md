# Docker Setup for Banking Voice App

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- At least 2GB RAM available for containers

### Running the Application

1. **Start all services:**
   ```bash
   ./docker-run.sh start
   ```

2. **Check application status:**
   ```bash
   ./docker-run.sh status
   ```

3. **View application logs:**
   ```bash
   ./docker-run.sh logs
   ```

4. **Health check:**
   ```bash
   ./docker-run.sh health
   ```

5. **Stop all services:**
   ```bash
   ./docker-run.sh stop
   ```

### Accessing the Application

- **Web Interface:** http://localhost:8000
- **Health Endpoint:** http://localhost:8000/health
- **API Documentation:** http://localhost:8000/docs

### Services

- **Banking App:** Port 8000
- **MongoDB:** Port 27017

### Docker Components

- **banking-voice-app:** Main application container (FastAPI)
- **banking_voice_mongodb:** MongoDB database container
- **Networks:** All services run on `banking-voice-app_banking_network`

### Environment Variables

The application uses these environment variables in Docker:

- `MONGODB_URL`: Connection string to MongoDB
- `DATABASE_NAME`: Database name (default: banking_voice_app)
- `API_HOST`: Host address (default: 0.0.0.0)
- `API_PORT`: Port number (default: 8000)
- `DEBUG`: Debug mode (default: false)

### Troubleshooting

1. **Port conflicts:** If port 8000 is in use, modify the port mapping in `docker-run.sh`
2. **MongoDB connection issues:** Ensure MongoDB container is healthy before starting the app
3. **Container logs:** Use `./docker-run.sh logs` to debug issues

### Manual Docker Commands

If you prefer manual control:

```bash
# Start MongoDB
docker-compose up -d mongodb

# Build application image
docker build -t banking-voice-app .

# Run application
docker run -d --name banking-app \
  --network banking-voice-app_banking_network \
  -p 8000:8000 \
  -e MONGODB_URL="mongodb://admin:password123@banking_voice_mongodb:27017/banking_voice_app?authSource=admin" \
  banking-voice-app
```

### Production Considerations

For production deployment:

1. **Security:** Change MongoDB credentials in `docker-compose.yml`
2. **Persistence:** Database data is stored in Docker volumes
3. **Scaling:** Use Docker Swarm or Kubernetes for multiple replicas
4. **Monitoring:** Add health checks and monitoring tools
5. **SSL:** Configure HTTPS and SSL certificates

### Development with Docker

For development, you can mount source code:

```bash
docker run -d --name banking-app-dev \
  --network banking-voice-app_banking_network \
  -p 8000:8000 \
  -v $(pwd)/app:/app/app \
  -e DEBUG="true" \
  banking-voice-app
```