document.addEventListener('DOMContentLoaded', function() {
    const elements = {
        videoUrl: document.getElementById('videoUrl'),
        processBtn: document.getElementById('processBtn'),
        loading: document.getElementById('loading'),
        results: document.getElementById('results'),
        chatHistory: document.getElementById('chatHistory'),
        questionInput: document.getElementById('questionInput'),
        askBtn: document.getElementById('askBtn')
    };
    
    let currentTranscript = '';
    let chatHistory = [];

    function addMessageToChat(content, type = 'assistant') {
        const message = document.createElement('div');
        message.className = `chat-message ${type}`;
        
        // Add title for summary messages
        if (type === 'summary') {
            message.innerHTML = `<div class="message-title">- Summary -</div>${content}`;
        } else {
            message.textContent = content;
        }
        
        elements.chatHistory.appendChild(message);
        elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
        
        // Save to chat history
        chatHistory.push({ content, type });
    }

    async function processVideo() {
        if (!elements.videoUrl.value) {
            showError('Please enter a YouTube URL');
            return;
        }

        toggleLoading(true);
        try {
            const response = await fetchWithError('/process', {
                video_url: elements.videoUrl.value
            });
            
            currentTranscript = response.transcript;
            
            // Clear chat history
            elements.chatHistory.innerHTML = '';
            chatHistory = [];
            
            // Add summary as first message
            addMessageToChat(response.summary, 'summary');
            elements.results.style.display = 'block';
        } catch (error) {
            showError(error);
        } finally {
            toggleLoading(false);
        }
    }

    async function askQuestion() {
        const question = elements.questionInput.value.trim();
        if (!question) {
            showError('Please enter a question');
            return;
        }

        // Add user question to chat
        addMessageToChat(question, 'user');
        
        elements.askBtn.disabled = true;
        elements.questionInput.value = '';
        
        try {
            const response = await fetchWithError('/ask', {
                question: question,
                transcript: currentTranscript
            });
            
            // Add assistant response to chat
            addMessageToChat(response.answer);
        } catch (error) {
            showError(error);
        } finally {
            elements.askBtn.disabled = false;
        }
    }

    async function fetchWithError(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (!response.ok) {
            throw result.error || 'An error occurred';
        }
        return result;
    }

    function toggleLoading(show) {
        elements.loading.style.display = show ? 'block' : 'none';
        elements.results.style.display = show ? 'none' : 'block';
        elements.processBtn.disabled = show;
    }

    function showError(message) {
        alert(message);
    }

    // Add click event listeners
    elements.processBtn.addEventListener('click', processVideo);
    elements.askBtn.addEventListener('click', askQuestion);
    
    // Add enter key support for URL input
    elements.videoUrl.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !elements.processBtn.disabled) {
            processVideo();
        }
    });
    
    // Add enter key support for question input
    elements.questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !elements.askBtn.disabled) {
            askQuestion();
        }
    });
}); 