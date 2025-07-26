// Mathly AI Math Assistant - Frontend Logic
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatBox = document.getElementById('chat-box');

    // Handle user input submission
    function handleSubmit() {
        const message = userInput.value.trim();
        if (message === '') return;

        // Add user message to chat
        addMessage(message, 'user');
        userInput.value = '';

        // Show typing indicator
        const loadingIndicator = addLoadingIndicator();

        // Send message to backend
        sendMessageToBackend(message)
            .then(response => {
                // Remove loading indicator
                loadingIndicator.remove();
                
                // Add bot response to chat
                addMessage(response, 'bot');
                
                // Render math formulas if any
                if (window.MathJax) {
                    window.MathJax.typeset();
                }
            })
            .catch(error => {
                // Remove loading indicator
                loadingIndicator.remove();
                
                // Add error message
                addMessage("Sorry, I encountered an error. Please try again.", 'bot');
                console.error('Error:', error);
            });
    }

    // Add event listeners
    sendButton.addEventListener('click', handleSubmit);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    });

    // Function to add a message to the chat box
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        // Process math syntax in the text
        if (sender === 'bot') {
            // Replace math expressions with LaTeX format for MathJax
            text = processMathSyntax(text);
        }
        
        messageDiv.innerHTML = text;
        chatBox.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Function to add loading indicator
    function addLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatBox.appendChild(loadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        return loadingDiv;
    }

    // Function to send message to backend
    async function sendMessageToBackend(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error communicating with backend:', error);
            return "I'm having trouble connecting to my brain. Please try again in a moment.";
        }
    }

    // Function to process math syntax
    function processMathSyntax(text) {
        // Replace simple math expressions with LaTeX format
        // This is a basic implementation, can be enhanced for more complex expressions
        text = text.replace(/\$([^$]+)\$/g, '\\($1\\)');
        
        // Handle common math symbols
        const symbolMap = {
            'sqrt': '√',
            '^2': '²',
            '^3': '³',
            '->': '→',
            '>=': '≥',
            '<=': '≤',
            '!=': '≠'
        };
        
        // Replace symbols
        for (const [symbol, replacement] of Object.entries(symbolMap)) {
            text = text.replace(new RegExp(symbol, 'g'), replacement);
        }
        
        return text;
    }

    // Initialize with focus on input
    userInput.focus();
});