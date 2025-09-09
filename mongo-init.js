// MongoDB initialization script for banking voice app
db = db.getSiblingDB('banking_voice_app');

// Create the voice_actions collection
db.createCollection('voice_actions');

// Create indexes for better performance
db.voice_actions.createIndex({ "userId": 1 });
db.voice_actions.createIndex({ "timestamp": 1 });
db.voice_actions.createIndex({ "userId": 1, "timestamp": -1 });

// Insert a sample document (optional)
db.voice_actions.insertOne({
    "userId": "sample-user-id",
    "audioTranscript": "Sample banking request for testing",
    "audioFileName": "sample.wav",
    "processed": false,
    "timestamp": new Date()
});

print("Banking Voice App database initialized successfully!");