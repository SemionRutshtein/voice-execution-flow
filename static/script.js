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

            // Send to new voice processing endpoint
            await this.processVoiceMessage(audioBlob);

        } catch (error) {
            console.error('Error processing audio:', error);
            this.showError(`Failed to process audio: ${error.message}`);
            this.updateStatus('Ready to record your banking request');
        } finally {
            this.resetRecordingState();
        }
    }

    async processVoiceMessage(audioBlob) {
        try {
            // Create form data for voice processing
            const formData = new FormData();
            formData.append('audio', audioBlob, `recording_${Date.now()}.webm`);
            formData.append('userId', this.userId);

            // Send to voice processing endpoint
            const response = await fetch('/api/process-voice', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Processing failed: ${response.status}`);
            }

            const result = await response.json();

            // Show processing result
            this.showProcessingResult(result);

            this.updateStatus('Voice message processed successfully!');

        } catch (error) {
            console.error('Error processing voice message:', error);
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
    
    showProcessingResult(result) {
        // Show the processing result with detected language and URL
        if (result.success && result.n8nResult && result.n8nResult.success) {
            // Show detected language
            if (result.detectedLanguage) {
                this.transcriptionText.textContent = `Language detected: ${result.detectedLanguage}`;
                this.transcriptionResult.classList.remove('hidden');
            }

            // Display N8N processing result with URL
            this.displayN8nResult(result.n8nResult);
        } else {
            this.showError(result.n8nResult?.error || 'Failed to process voice message');
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
            const url = n8nData.result?.url || null;
            const message = n8nData.result?.message || '';
            const isFallback = n8nData.result?.fallback || false;

            resultHtml = `
                <div class="n8n-success">
                    <div class="n8n-status">✅ Processing completed successfully</div>
                    <div class="n8n-timing">Processing time: ${n8nData.processingTime?.toFixed(2) || 'N/A'}s</div>
                    ${url ? `
                        <div class="n8n-url-result">
                            <strong>Result URL:</strong>
                            <div class="url-container">
                                <a href="${url}" target="_blank" rel="noopener noreferrer" class="result-url">${url}</a>
                                <button onclick="navigator.clipboard.writeText('${url}')" class="copy-button" title="Copy URL">📋</button>
                            </div>
                        </div>
                    ` : ''}
                    ${message ? `
                        <div class="n8n-message">
                            <strong>Message:</strong> ${message}
                        </div>
                    ` : ''}
                    ${isFallback ? `
                        <div class="fallback-notice">
                            <small>⚠️ This is a fallback response. Configure N8N workflow for full functionality.</small>
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