// Mathly AI Math Assistant - Chat Interface Logic
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const cameraBtn = document.getElementById('camera-btn');
    const cameraModal = document.getElementById('camera-modal');
    const cameraClose = document.querySelector('.camera-close');
    const cameraFeed = document.getElementById('camera-feed');
    const cameraCanvas = document.getElementById('camera-canvas');
    const captureBtn = document.getElementById('capture-btn');
    const retakeBtn = document.getElementById('retake-btn');
    const sendImageBtn = document.getElementById('send-image-btn');
    
    let stream = null;
    let capturedImage = null;
    
    // Initialize animated background effects
    initAnimatedBackground();
    
    // Initialize MathJax
    window.MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']]
        },
        svg: {
            fontCache: 'global'
        }
    };
    
    // Function to add a message to the chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process the message content
        let processedMessage = message;
        
        console.log("Adding message:", processedMessage);
        
        // Add the message to the content div
        contentDiv.innerHTML = `<p>${processedMessage}</p>`;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Process MathJax rendering
        if (window.MathJax) {
            try {
                console.log("Typesetting MathJax content");
                window.MathJax.typesetPromise([contentDiv])
                    .catch((err) => {
                        console.error('MathJax error:', err);
                        // If MathJax fails, still show the content
                        contentDiv.innerHTML = `<p>Error rendering math. Raw content: ${processedMessage}</p>`;
                    });
            } catch (err) {
                console.error('MathJax processing error:', err);
            }
        }
        
        // Scroll to the bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to show loading indicator
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot';
        loadingDiv.id = 'loading-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content loading-indicator';
        
        contentDiv.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        
        loadingDiv.appendChild(contentDiv);
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to hide loading indicator
    function hideLoading() {
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
    
    // Function to send a message to the backend
    async function sendMessage(message, isImage = false) {
        if (!message) return;
        
        // Add user message to chat
        if (!isImage) {
            addMessage(message, true);
        } else {
            addMessage("📷 I've sent a picture of my math problem.", true);
        }
        
        // Clear input field
        userInput.value = '';
        
        // Show loading indicator
        showLoading();
        
        try {
            // Define base URL with the correct port
            const baseUrl = 'http://localhost:5001';
            let endpoint = '/api/chat';
            let payload = {};
            
            if (isImage) {
                endpoint = '/api/image';
                payload = { image: message };
            } else {
                payload = { input: message };
            }
            
            console.log(`Sending request to ${baseUrl}${endpoint}:`, payload);
            
            const response = await fetch(`${baseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            console.log("Response status:", response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("Received data:", data);
            
            // Hide loading indicator
            hideLoading();
            
            if (data.response) {
                // Add bot response to chat
                console.log("Bot response:", data.response);
                addMessage(data.response);
                
                // Add step-by-step solution if available
                if (data.steps && data.steps.length > 0) {
                    console.log("Solution steps:", data.steps);
                    const stepsDiv = document.createElement('div');
                    stepsDiv.className = 'solution-steps';
                    
                    let stepsHtml = '<strong>Step-by-step solution:</strong>';
                    data.steps.forEach((step, index) => {
                        stepsHtml += `
                            <div class="solution-step">
                                <span class="solution-step-number">Step ${index + 1}:</span> ${step}
                            </div>
                        `;
                    });
                    
                    const lastMessage = chatMessages.lastElementChild.querySelector('.message-content');
                    lastMessage.innerHTML += stepsHtml;
                    
                    // Re-process MathJax rendering
                    if (window.MathJax) {
                        try {
                            window.MathJax.typesetPromise([lastMessage])
                                .catch((err) => console.error('MathJax error with steps:', err));
                        } catch (err) {
                            console.error('MathJax processing error with steps:', err);
                        }
                    }
                }
            } else if (data.error) {
                // Add error message
                console.error("Server reported error:", data.error);
                addMessage(`Sorry, I encountered an error: ${data.error}`);
            } else {
                // No recognized response format
                console.warn("Unrecognized response format:", data);
                addMessage("Sorry, I received a response but couldn't understand it. Please try again.");
            }
        } catch (error) {
            // Hide loading indicator
            hideLoading();
            
            // Add error message
            console.error('Error during message processing:', error);
            addMessage(`Sorry, I had trouble connecting to the server: ${error.message}. Please try again later.`);
        }
    }
    
    // Event listeners for sending messages
    sendBtn.addEventListener('click', () => sendMessage(userInput.value.trim()));
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage(userInput.value.trim());
        }
    });
    
    // Camera functionality
    function openCamera() {
        cameraModal.style.display = 'flex';
        
        // Request camera access with specific constraints for better compatibility
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'environment' // Prefer back camera if available
            }
        };
        
        // Request camera access
        navigator.mediaDevices.getUserMedia(constraints)
            .then(mediaStream => {
                stream = mediaStream;
                cameraFeed.srcObject = stream;
                // Ensure video is visible and plays correctly
                cameraFeed.style.display = 'block';
                cameraFeed.play().catch(e => console.error('Error playing video:', e));
                
                captureBtn.style.display = 'block';
                retakeBtn.style.display = 'none';
                sendImageBtn.style.display = 'none';
                cameraCanvas.style.display = 'none';
            })
            .catch(err => {
                console.error('Error accessing camera:', err);
                addMessage('Sorry, I couldn\'t access your camera. Please check permissions and try again.');
                closeCamera();
            });
    }
    
    function closeCamera() {
        cameraModal.style.display = 'none';
        
        // Stop all video streams
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }
    
    function captureImage() {
        const context = cameraCanvas.getContext('2d');
        
        // Set canvas dimensions to match video
        cameraCanvas.width = cameraFeed.videoWidth;
        cameraCanvas.height = cameraFeed.videoHeight;
        
        // Draw current video frame to canvas
        context.drawImage(cameraFeed, 0, 0, cameraCanvas.width, cameraCanvas.height);
        
        // Hide video and show canvas
        cameraFeed.style.display = 'none';
        cameraCanvas.style.display = 'block';
        
        // Show retake and send buttons, hide capture button
        captureBtn.style.display = 'none';
        retakeBtn.style.display = 'block';
        sendImageBtn.style.display = 'block';
        
        // Get base64 image data
        capturedImage = cameraCanvas.toDataURL('image/jpeg');
    }
    
    function sendCapturedImage() {
        if (!capturedImage) return;
        
        closeCamera();
        sendMessage(capturedImage, true);
        capturedImage = null;
    }
    
    // Camera button event listeners
    cameraBtn.addEventListener('click', openCamera);
    cameraClose.addEventListener('click', closeCamera);
    captureBtn.addEventListener('click', captureImage);
    retakeBtn.addEventListener('click', () => {
        cameraFeed.style.display = 'block';
        cameraCanvas.style.display = 'none';
        captureBtn.style.display = 'block';
        retakeBtn.style.display = 'none';
        sendImageBtn.style.display = 'none';
        capturedImage = null;
    });
    sendImageBtn.addEventListener('click', sendCapturedImage);
    
    // Add animated background effects for the chat interface
    function initAnimatedBackground() {
        // Make the background shapes respond to mouse movement
        window.addEventListener('mousemove', (e) => {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            document.querySelectorAll('.chat-bg-shape').forEach((shape, index) => {
                const speed = 0.03 + (index * 0.01);
                const offsetX = (x * speed * 100);
                const offsetY = (y * speed * 100);
                
                shape.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${1 + (y * 0.03)})`;
            });
        });
        
        // Add floating math symbols dynamically
        const mathSymbols = ['∫', 'π', '∑', '√', '×', '÷', 'θ', '∞', '+', '−', '=', 'α', 'β', 'Δ', 'λ'];
        const body = document.querySelector('body');
        
        for (let i = 0; i < 8; i++) {
            const symbol = document.createElement('div');
            symbol.className = 'math-symbol';
            symbol.textContent = mathSymbols[Math.floor(Math.random() * mathSymbols.length)];
            symbol.style.left = `${Math.random() * 90 + 5}%`;
            symbol.style.top = `${Math.random() * 40}%`;
            symbol.style.animationDuration = `${Math.random() * 20 + 30}s`;
            symbol.style.animationDelay = `${Math.random() * 10}s`;
            symbol.style.opacity = '0';
            symbol.style.fontSize = `${Math.random() * 1.5 + 1}rem`;
            body.appendChild(symbol);
        }
    }
    
    // Initialize animated background
    initAnimatedBackground();
    
    // Focus input field on load
    userInput.focus();
});
