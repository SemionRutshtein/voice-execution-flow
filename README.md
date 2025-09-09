# Voice Execution Flow

A banking voice assistant application that processes voice commands for banking operations using speech recognition and natural language processing.

## Features

- 🎤 **Voice Recording**: Web-based voice recording interface
- 🔊 **Audio Processing**: Supports multiple audio formats (WebM, WAV, MP3, OGG)
- 🧠 **Speech Recognition**: Google Speech-to-Text integration
- 💾 **Data Persistence**: MongoDB storage for voice actions
- 🐳 **Docker Support**: Fully containerized application
- 🌐 **Web Interface**: Modern, responsive UI

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: HTML/CSS/JavaScript
- **Database**: MongoDB
- **Audio Processing**: FFmpeg + FLAC + pydub
- **Speech Recognition**: Google Speech Recognition API
- **Containerization**: Docker + Docker Compose

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. Clone the repository:
```bash
git clone https://github.com/SemionRutshtein/voice-execution-flow.git
cd voice-execution-flow
```

2. Start the application:
```bash
docker-compose up --build
```

3. Open your browser and navigate to:
```
http://localhost:8000
```

## API Endpoints

### Health Check
```http
GET /health
```

### Upload Audio
```http
POST /api/upload-audio
Content-Type: multipart/form-data

Parameters:
- file: Audio file (WebM, WAV, MP3, OGG)
- user_id: User identifier (optional)
```

### Get User Actions
```http
GET /api/user/{user_id}/actions
```

### Get Specific Action
```http
GET /api/action/{action_id}
```

### Generate Session
```http
POST /api/generate-session
```

## Project Structure

```
banking-voice-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # MongoDB connection
│   ├── config.py            # Configuration settings
│   └── audio_processor.py   # Audio processing logic
├── static/
│   ├── index.html          # Web interface
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
├── docker-compose.yml      # Docker services
├── Dockerfile             # App container
├── requirements.txt       # Python dependencies
├── mongo-init.js         # MongoDB initialization
└── README.md
```

## Technical Details

### Audio Processing Pipeline
1. **Upload**: Web interface captures audio or accepts file upload
2. **Conversion**: FFmpeg converts to WAV format if needed
3. **Transcription**: Google Speech Recognition processes audio
4. **Storage**: MongoDB stores transcription and metadata
5. **Response**: JSON response with transcription results

### Dependencies
- **FastAPI**: Modern web framework
- **PyMongo**: MongoDB driver
- **SpeechRecognition**: Speech-to-text processing
- **pydub**: Audio manipulation
- **FFmpeg**: Audio/video processing
- **FLAC**: Audio codec for speech recognition

## Configuration

Environment variables can be configured in `app/config.py`:

- `MONGODB_URL`: MongoDB connection string
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `MAX_AUDIO_FILE_SIZE`: Maximum file size for uploads
- `TEMP_AUDIO_DIR`: Temporary audio storage directory

## Development

### Local Development Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB:
```bash
docker run -d -p 27017:27017 mongo:7.0
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## Troubleshooting

### Common Issues

1. **FLAC conversion errors**: Ensure FLAC codec is installed
2. **MongoDB connection**: Verify MongoDB is running and accessible
3. **Audio format support**: Check FFmpeg installation for codec support
4. **Microphone access**: Ensure browser has microphone permissions

### Docker Issues

- Clean rebuild: `docker-compose down && docker-compose up --build`
- View logs: `docker-compose logs banking_app`
- Check containers: `docker-compose ps`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please create an issue on GitHub.

---

Built with ❤️ using FastAPI, MongoDB, and modern web technologies.