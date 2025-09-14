# Banking Voice AI Assistant

An advanced banking voice assistant application that processes voice commands using AI-powered speech recognition and natural language processing through N8N workflows.

## ✨ Features

- 🎤 **Voice Recording**: Web-based voice recording interface
- 🔊 **Audio Processing**: Supports multiple audio formats (WebM, WAV, MP3, OGG)
- 🤖 **AI-Powered Processing**: OpenAI Whisper for speech-to-text + GPT-4 for intelligent responses
- 🔄 **N8N Workflow Integration**: Automated AI processing pipeline
- 💾 **Data Persistence**: MongoDB storage for voice actions and history
- 🐳 **Docker Support**: Fully containerized application stack
- 🌐 **Modern Web Interface**: Responsive UI with real-time feedback

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: HTML/CSS/JavaScript (No local transcription)
- **AI Workflow Engine**: N8N with OpenAI integration
- **Database**: MongoDB
- **Speech-to-Text**: OpenAI Whisper API
- **AI Assistant**: OpenAI GPT-4
- **Audio Processing**: FFmpeg + FLAC + pydub
- **Containerization**: Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose
- OpenAI API Key

### Running the Application

1. Clone the repository:
```bash
git clone https://github.com/SemionRutshtein/voice-execution-flow.git
cd banking-voice-app
```

2. Start all services:
```bash
./docker-run.sh start
```
*Or manually:*
```bash
docker-compose up -d
```

3. **Setup N8N AI Workflow** (Required - 5 minutes):
   - Open N8N interface: http://localhost:5678
   - Follow the complete guide in `setup-n8n-workflow.md`
   - Use your OpenAI API key for Whisper + GPT-4 integration

4. Open the banking assistant:
```
http://localhost:8000
```

### 🎯 How It Works
**User Voice** → **Frontend** → **Backend** → **N8N** → **OpenAI (Whisper + GPT-4)** → **AI Response** → **User**

## 📋 API Endpoints

### Health Check
```http
GET /health
Response: {"status":"healthy","message":"Banking Voice Action API is running"}
```

### Voice Message Processing (AI Webhook)
```http
POST /api/webhook/voice-message
Content-Type: multipart/form-data

Parameters:
- audio: Audio file (WebM, WAV, MP3, OGG)
- userId: User identifier
- timestamp: Request timestamp (optional)

Response: AI-processed result with transcript and banking assistance
```

### Get User Actions History
```http
GET /api/user/{user_id}/actions?limit=100
```

### Get Specific Action
```http
GET /api/action/{action_id}
```

### Generate Session
```http
POST /api/generate-session
Response: {"userId": "generated-uuid"}
```

## 🌐 Service URLs

- **Banking App**: http://localhost:8000
- **N8N Workflow Engine**: http://localhost:5678
- **MongoDB**: localhost:27017

## 📁 Project Structure

```
banking-voice-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application with N8N integration
│   ├── models.py            # Pydantic models
│   ├── database.py          # MongoDB connection
│   ├── config.py            # Configuration settings
│   ├── n8n_service.py       # N8N workflow integration
│   └── audio_processor.py   # Audio processing utilities
├── static/
│   ├── index.html          # Web interface
│   ├── style.css           # Styling
│   └── script.js           # Frontend (no local transcription)
├── docker-compose.yml      # Docker services (App + N8N + MongoDB)
├── Dockerfile             # App container
├── requirements.txt       # Python dependencies
├── mongo-init.js         # MongoDB initialization
├── docker-run.sh         # Service management script
├── setup-n8n-workflow.md # N8N workflow setup guide
├── DOCKER.md             # Docker documentation
├── INTEGRATION_COMPLETE.md # Integration completion guide
└── README.md
```

## 🔄 AI Processing Pipeline

1. **Voice Capture**: Web interface records user voice
2. **Audio Upload**: Frontend sends raw audio to backend webhook
3. **N8N Workflow**: Backend forwards audio to N8N automation
4. **AI Processing**: N8N triggers OpenAI Whisper (speech-to-text) + GPT-4 (AI response)
5. **Response**: AI-generated banking assistance returned to user
6. **Storage**: MongoDB stores interaction history and transcripts

## 🛠️ Technology Stack

### Backend Services
- **FastAPI**: Modern Python web framework
- **N8N**: Visual workflow automation for AI processing
- **MongoDB**: Document database for data persistence
- **Docker**: Containerization platform

### AI & Processing
- **OpenAI Whisper**: Advanced speech-to-text
- **OpenAI GPT-4**: Intelligent banking assistant responses
- **FFmpeg + FLAC**: Audio format conversion
- **pydub**: Python audio manipulation

## ⚙️ Configuration

Environment variables in Docker Compose:

**Banking App:**
- `MONGODB_URL`: MongoDB connection string
- `N8N_WEBHOOK_URL`: N8N webhook endpoint for AI processing
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `MAX_AUDIO_FILE_SIZE`: Maximum audio file size
- `TEMP_AUDIO_DIR`: Temporary audio storage

**N8N Service:**
- `N8N_BASIC_AUTH_ACTIVE`: false (authentication disabled)
- `N8N_HOST`: 0.0.0.0
- `N8N_PORT`: 5678

## 🧑‍💻 Management Commands

### Start/Stop Services
```bash
./docker-run.sh start    # Start all services
./docker-run.sh stop     # Stop all services
./docker-run.sh status   # Check service status
./docker-run.sh logs     # View application logs
./docker-run.sh health   # Health check
```

### Manual Docker Commands
```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop and remove
docker-compose build              # Rebuild images
docker logs banking_voice_app     # App logs
docker logs banking_voice_n8n     # N8N logs
```

## 🔧 Troubleshooting

### Common Issues

1. **N8N Workflow Not Set Up**:
   - Go to http://localhost:5678
   - Follow `setup-n8n-workflow.md` guide
   - Ensure OpenAI API key is correctly configured

2. **Audio Processing Fails**:
   - Verify OpenAI API key is valid and has credits
   - Check N8N workflow is active (toggle switch)
   - Ensure audio file format is supported

3. **Services Won't Start**:
   - Check port conflicts (8000, 5678, 27017)
   - Verify Docker has enough resources allocated
   - Clean restart: `./docker-run.sh stop && ./docker-run.sh start`

4. **MongoDB Connection Issues**:
   - Verify MongoDB container is healthy: `docker-compose ps`
   - Check MongoDB logs: `docker logs banking_voice_mongodb`

5. **Browser Issues**:
   - Ensure microphone permissions are granted
   - Use modern browser (Chrome, Firefox, Safari, Edge)
   - Check HTTPS/HTTP mixed content warnings

### Debug Commands

```bash
# Check all service status
docker-compose ps

# View detailed logs
docker logs banking_voice_app -f
docker logs banking_voice_n8n -f
docker logs banking_voice_mongodb -f

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:5678/healthz

# Complete restart
./docker-run.sh stop && ./docker-run.sh start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker: `./docker-run.sh start`
5. Submit a pull request

### Development Notes
- Frontend changes: Edit `static/` files (hot reload)
- Backend changes: Rebuild container `docker-compose build banking_app`
- N8N workflows: Export from UI and document in `setup-n8n-workflow.md`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Example Voice Commands

Try these banking commands with your voice:

- *"What is my account balance?"*
- *"How do I transfer money to my savings account?"*
- *"I need to set up a recurring payment"*
- *"Help me understand my recent transactions"*
- *"How do I dispute a charge?"*

## 🆘 Support

For issues and questions:
1. Check `INTEGRATION_COMPLETE.md` for setup help
2. Review `setup-n8n-workflow.md` for N8N configuration
3. Create an issue on GitHub

---

🤖 Built with AI: **FastAPI** + **N8N** + **OpenAI** + **MongoDB** + **Docker**