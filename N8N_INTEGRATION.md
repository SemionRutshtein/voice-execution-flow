# N8N Webhook Integration

This feature adds n8n webhook integration for processing voice messages through automated workflows.

## Features Added

### 1. Voice Message Webhook Endpoint
- **Endpoint**: `POST /api/webhook/voice-message`
- **Purpose**: Receives voice messages and processes them through n8n workflows
- **Request Format**:
  ```json
  {
    "userId": "user-session-id",
    "audioTranscript": "transcribed voice message",
    "audioFileName": "optional-audio-file.wav"
  }
  ```

### 2. N8N Service Integration
- Automatic processing of voice messages through n8n workflows
- Configurable webhook URL and timeout settings
- Error handling and response processing
- Processing time tracking

### 3. Enhanced UI Display
- Real-time display of n8n processing results
- Success/failure status indicators
- Processing time display
- Full n8n response data visualization

## Configuration

### Environment Variables
```bash
N8N_WEBHOOK_URL=http://localhost:5678/webhook/voice-process
N8N_TIMEOUT=30
```

### N8N Workflow Setup
1. Create a webhook trigger in n8n with the path `/webhook/voice-process`
2. Configure workflow to process the incoming voice data
3. Return appropriate response data

## Usage

### Running with Docker Compose
```bash
# Start the full stack including n8n
docker-compose -f docker-compose.n8n.yml up -d

# Access services:
# App: http://localhost:8000
# N8N: http://localhost:5678
# MongoDB: localhost:27017
```

### API Integration
The voice webhook automatically integrates with both:
1. **Audio Upload Flow**: When users upload audio files
2. **Direct Webhook**: For external systems sending voice data

### Response Format
```json
{
  "success": true,
  "message": "Voice message processed",
  "actionId": "mongodb-document-id",
  "n8nResult": {
    "success": true,
    "result": {
      // n8n workflow response data
    },
    "error": null,
    "processingTime": 1.23
  }
}
```

## Development Notes

- The n8n service runs in a separate Docker container
- Voice messages are processed asynchronously
- All processing results are stored in MongoDB
- The frontend displays real-time processing status
- Failed n8n processing doesn't prevent voice action storage

## Testing

1. Start the services with docker-compose
2. Record a voice message in the app
3. Check the n8n processing result displayed in the UI
4. Verify the data is stored in MongoDB with processing status