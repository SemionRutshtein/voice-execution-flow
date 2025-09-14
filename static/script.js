class VoiceBankingApp {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.userId = null;
        this.recordingStartTime = null;
        this.timerInterval = null;
        
        // DOM elements
        this.recordButton = document.getElementById('recordButton');
        this.statusMessage = document.getElementById('statusMessage');
        this.recordingTimer = document.getElementById('recordingTimer');
        this.transcriptionResult = document.getElementById('transcriptionResult');
        this.transcriptionText = document.getElementById('transcriptionText');
        this.errorMessage = document.getElementById('errorMessage');
        this.errorText = document.getElementById('errorText');
        this.showHistoryButton = document.getElementById('showHistoryButton');
        this.historyContainer = document.getElementById('historyContainer');
        this.historyList = document.getElementById('historyList');
        this.n8nResult = document.getElementById('n8nResult');
        this.n8nResultContent = document.getElementById('n8nResultContent');
        
        this.init();
    }
    
    async init() {
        // Generate or retrieve user session
        await this.initializeSession();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initial status
        this.updateStatus('Ready to record your banking request');
        
        // Check browser compatibility
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showError('Your browser does not support audio recording. Please use a modern browser.');
            return;
        }
    }
    
    async initializeSession() {
        // Check if we have a stored user ID
        this.userId = localStorage.getItem('bankingUserId');
        
        if (!this.userId) {
            try {
                const response = await fetch('/api/generate-session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.userId = data.userId;
                    localStorage.setItem('bankingUserId', this.userId);
                } else {
                    throw new Error('Failed to generate session');
                }
            } catch (error) {
                console.error('Error generating session:', error);
                // Generate a fallback UUID
                this.userId = this.generateUUID();
                localStorage.setItem('bankingUserId', this.userId);
            }
        }
    }
    
    setupEventListeners() {
        this.recordButton.addEventListener('click', () => {
            if (!this.isRecording) {
                this.startRecording();
            } else {
                this.stopRecording();
            }
        });
        
        this.showHistoryButton.addEventListener('click', () => {
            this.toggleHistory();
        });
        
        // Keyboard accessibility
        this.recordButton.addEventListener('keydown', (e) => {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                this.recordButton.click();
            }
        });
    }
    
    async startRecording() {
        try {
            this.hideMessages();
            this.updateStatus('Requesting microphone access...');
            
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                } 
            });
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: this.getSupportedMimeType()
            });
            
            this.audioChunks = [];
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processAudioRecording();
            };
            
            this.mediaRecorder.start(1000); // Collect data every second
            
            this.updateRecordingUI();
            this.startTimer();
            this.updateStatus('Recording... Click again to stop');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Could not access microphone. Please check permissions and try again.');
            this.resetRecordingState();
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;
            this.stopTimer();
            this.updateProcessingUI();
            this.updateStatus('Processing your audio...');
        }
    }
    
    async processAudioRecording() {
        try {
            if (this.audioChunks.length === 0) {
                throw new Error('No audio data recorded');
            }

            const audioBlob = new Blob(this.audioChunks, {
                type: this.mediaRecorder.mimeType
            });

            // Send directly to N8N webhook for processing
            await this.sendToN8NWebhook(audioBlob);

        } catch (error) {
            console.error('Error processing audio:', error);
            this.showError(`Failed to process audio: ${error.message}`);
            this.updateStatus('Ready to record your banking request');
        } finally {
            this.resetRecordingState();
        }
    }

    async sendToN8NWebhook(audioBlob) {
        try {
            // Create form data for N8N webhook
            const formData = new FormData();
            formData.append('audio', audioBlob, `recording_${Date.now()}.webm`);
            formData.append('userId', this.userId);
            formData.append('timestamp', new Date().toISOString());

            // Send to N8N webhook
            const response = await fetch('/api/webhook/voice-message', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Processing failed: ${response.status}`);
            }

            const result = await response.json();

            // Show AI response from N8N
            this.showAIResponse(result);

            this.updateStatus('Audio processed successfully by AI!');

            // Refresh history
            setTimeout(() => this.loadHistory(), 1000);

        } catch (error) {
            console.error('Error sending to N8N webhook:', error);
            throw error;
        }
    }
    
    updateRecordingUI() {
        this.recordButton.classList.add('recording');
        this.recordButton.querySelector('.button-text').textContent = 'Recording...';
        this.recordingTimer.classList.remove('hidden');
    }
    
    updateProcessingUI() {
        this.recordButton.classList.remove('recording');
        this.recordButton.classList.add('processing');
        this.recordButton.querySelector('.button-text').textContent = 'Processing...';
        this.recordingTimer.classList.add('hidden');
    }
    
    resetRecordingState() {
        this.recordButton.classList.remove('recording', 'processing');
        this.recordButton.querySelector('.button-text').textContent = 'Press to Record';
        this.recordingTimer.classList.add('hidden');
        this.isRecording = false;
        this.audioChunks = [];
    }
    
    startTimer() {
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            this.recordingTimer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    updateStatus(message) {
        this.statusMessage.textContent = message;
    }
    
    showAIResponse(result) {
        // Show the AI transcription and response
        if (result.n8nResult && result.n8nResult.success) {
            // Show transcription from AI
            if (result.actionData && result.actionData.audioTranscript) {
                this.transcriptionText.textContent = result.actionData.audioTranscript;
                this.transcriptionResult.classList.remove('hidden');
            }

            // Display AI response
            this.displayN8nResult(result.n8nResult);
        } else {
            this.showError(result.n8nResult?.error || 'Failed to process with AI');
        }
        this.errorMessage.classList.add('hidden');
    }
    
    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.classList.remove('hidden');
        this.transcriptionResult.classList.add('hidden');
    }
    
    hideMessages() {
        this.transcriptionResult.classList.add('hidden');
        this.errorMessage.classList.add('hidden');
        this.n8nResult.classList.add('hidden');
    }

    displayN8nResult(n8nData) {
        if (!n8nData) {
            this.n8nResult.classList.add('hidden');
            return;
        }

        let resultHtml = '';

        if (n8nData.success) {
            resultHtml = `
                <div class="n8n-success">
                    <div class="n8n-status">✅ Processing completed successfully</div>
                    <div class="n8n-timing">Processing time: ${n8nData.processingTime?.toFixed(2) || 'N/A'}s</div>
                    ${n8nData.result ? `
                        <div class="n8n-response">
                            <strong>Response:</strong>
                            <pre>${JSON.stringify(n8nData.result, null, 2)}</pre>
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            resultHtml = `
                <div class="n8n-error">
                    <div class="n8n-status">❌ Processing failed</div>
                    <div class="n8n-timing">Processing time: ${n8nData.processingTime?.toFixed(2) || 'N/A'}s</div>
                    ${n8nData.error ? `
                        <div class="n8n-error-message">
                            <strong>Error:</strong> ${n8nData.error}
                        </div>
                    ` : ''}
                </div>
            `;
        }

        this.n8nResultContent.innerHTML = resultHtml;
        this.n8nResult.classList.remove('hidden');
    }
    
    async toggleHistory() {
        if (this.historyContainer.classList.contains('hidden')) {
            await this.loadHistory();
            this.historyContainer.classList.remove('hidden');
            this.showHistoryButton.textContent = 'Hide Previous Requests';
        } else {
            this.historyContainer.classList.add('hidden');
            this.showHistoryButton.textContent = 'Show Previous Requests';
        }
    }
    
    async loadHistory() {
        try {
            const response = await fetch(`/api/user/${this.userId}/actions`);
            
            if (!response.ok) {
                throw new Error('Failed to load history');
            }
            
            const actions = await response.json();
            this.displayHistory(actions);
            
        } catch (error) {
            console.error('Error loading history:', error);
            this.historyList.innerHTML = '<div class="history-item"><div class="history-item-text">Failed to load history</div></div>';
        }
    }
    
    displayHistory(actions) {
        if (actions.length === 0) {
            this.historyList.innerHTML = '<div class="history-item"><div class="history-item-text">No previous requests</div></div>';
            return;
        }
        
        this.historyList.innerHTML = actions.map(action => {
            const date = new Date(action.timestamp);
            const timeString = date.toLocaleString();
            
            return `
                <div class="history-item">
                    <div class="history-item-text">"${action.audioTranscript}"</div>
                    <div class="history-item-time">${timeString}</div>
                </div>
            `;
        }).join('');
    }
    
    getSupportedMimeType() {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/ogg;codecs=opus',
            'audio/mp4',
            'audio/wav'
        ];
        
        for (let type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }
        
        return 'audio/webm'; // Fallback
    }
    
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VoiceBankingApp();
});

// Service Worker registration (optional, for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}