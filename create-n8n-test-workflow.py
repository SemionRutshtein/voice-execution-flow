#!/usr/bin/env python3
"""
Quick script to create a test N8N workflow via the web interface
Since N8N API requires authentication, we'll provide a simple test workflow
"""

workflow_json = {
    "name": "Banking Voice Test Workflow",
    "active": True,
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "voice-process",
                "options": {}
            },
            "id": "webhook-node-123",
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1.1,
            "position": [240, 300],
            "webhookId": "voice-process"
        },
        {
            "parameters": {
                "respondWith": "json",
                "responseBody": """{
  "transcript": "Test response - workflow is working!",
  "aiResponse": "Hello! I am your banking assistant. The N8N workflow is now active and responding. Please set up the OpenAI integration for full functionality.",
  "userId": "test-user",
  "timestamp": "{{ $now }}",
  "success": true
}""",
                "options": {}
            },
            "id": "response-node-456",
            "name": "Respond to Webhook",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [460, 300]
        }
    ],
    "connections": {
        "Webhook": {
            "main": [
                [
                    {
                        "node": "Respond to Webhook",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}

print("=== N8N Quick Fix Workflow ===")
print("\n1. Open N8N: http://localhost:5678")
print("2. Click 'Add workflow' or '+'")
print("3. Click the 3-dot menu (⋮) → 'Import from JSON'")
print("4. Paste the following JSON:")
print("\n" + "="*50)
import json
print(json.dumps(workflow_json, indent=2))
print("="*50)
print("\n5. Save the workflow (Ctrl+S)")
print("6. IMPORTANT: Toggle the workflow to ACTIVE (switch in top-right)")
print("\n✅ This will fix the 404 error immediately!")
print("🔧 Then you can add OpenAI nodes for full AI functionality")