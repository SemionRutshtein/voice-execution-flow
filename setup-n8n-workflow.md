# N8N Banking Voice AI Workflow Setup

## Step 1: Access N8N Interface

1. Open your browser and go to: http://localhost:5678
2. N8N should load without authentication (auth is disabled in Docker setup)

## Step 2: Create the Voice Processing Workflow

### Create a New Workflow

1. Click "+ Create workflow" or "New Workflow"
2. Name it "Banking Voice AI Workflow"

### Add the Webhook Node

1. Click the "+" to add a node
2. Search for "Webhook" and select it
3. Configure the webhook:
   - **HTTP Method**: POST
   - **Path**: `voice-process`
   - **Response Mode**: "Respond when last node finishes"
4. Save the node

### Add OpenAI Audio Transcription Node

1. Add a new node after the Webhook
2. Search for "OpenAI" and select it
3. Configure the transcription:
   - **Resource**: Audio
   - **Operation**: Transcribe
   - **API Key**: `YOUR_OPENAI_API_KEY_HERE`
   - **Model**: whisper-1
   - **Binary Data**: Yes
   - **Binary Property Name**: `audio` (this matches what we send from frontend)
4. Save the node

### Add OpenAI Chat/Completion Node

1. Add another OpenAI node after transcription
2. Configure the chat:
   - **Resource**: Chat
   - **Operation**: Create a completion
   - **API Key**: `YOUR_OPENAI_API_KEY_HERE`
   - **Model**: gpt-4
   - **Messages**:
     ```json
     [
       {
         "role": "system",
         "content": "You are a helpful banking assistant AI. Analyze the user's voice request and provide appropriate banking guidance. Be concise, professional, and helpful. If the request is about account balance, transactions, transfers, or other banking operations, provide clear instructions on how to proceed safely. Always remind users to verify their identity through official banking channels for actual transactions."
       },
       {
         "role": "user",
         "content": "={{$node[\"OpenAI\"].json[\"text\"]}}"
       }
     ]
     ```
3. Save the node

### Add Response Node

1. Add a "Respond to Webhook" node at the end
2. Configure the response:
   - **Response Mode**: JSON
   - **Response Body**:
     ```json
     {
       "transcript": "={{$node[\"OpenAI\"].json[\"text\"]}}",
       "aiResponse": "={{$node[\"OpenAI1\"].json[\"choices\"][0][\"message\"][\"content\"]}}",
       "userId": "={{$node[\"Webhook\"].json[\"body\"][\"userId\"]}}",
       "timestamp": "={{$now}}",
       "success": true
     }
     ```
3. Save the node

### Connect the Nodes

1. Connect Webhook → OpenAI (Transcription)
2. Connect OpenAI (Transcription) → OpenAI (Chat)
3. Connect OpenAI (Chat) → Respond to Webhook

### Activate the Workflow

1. Click the toggle switch in the top-right to activate the workflow
2. The webhook should now be available at: `http://localhost:5678/webhook/voice-process`

## Step 3: Update Backend Configuration

The backend is already configured to send requests to:
- URL: `http://n8n:5678/webhook/voice-process` (internal Docker network)
- External URL: `http://localhost:5678/webhook/voice-process` (for testing)

## Step 4: Test the Integration

1. Start the complete application:
   ```bash
   docker-compose up -d
   ```

2. Access the web interface: http://localhost:8000

3. Try recording a voice message like:
   - "What is my account balance?"
   - "I want to transfer money to my savings account"
   - "How do I set up a recurring payment?"

## Troubleshooting

### If OpenAI nodes are not available:
1. Go to Settings → Community Nodes
2. Install the @n8n/n8n-nodes-openai package
3. Restart N8N container: `docker-compose restart n8n`

### If webhook is not receiving data:
1. Check the webhook URL in N8N matches what the backend is sending to
2. Verify the workflow is active (toggle switch on)
3. Check N8N logs: `docker logs banking_voice_n8n`

### If audio processing fails:
1. Verify the OpenAI API key is correct
2. Check that the binary property name is set to "audio"
3. Ensure the audio file is being sent correctly from frontend

## Expected Response Format

The N8N workflow should return:
```json
{
  "transcript": "What is my account balance?",
  "aiResponse": "To check your account balance, I recommend using your bank's official mobile app or website. You can also visit an ATM or call your bank's customer service line. For security, always verify your identity through official channels before accessing account information.",
  "userId": "user-id-here",
  "timestamp": "2024-01-01T12:00:00Z",
  "success": true
}
```

This response gets processed by the backend and displayed in the frontend.