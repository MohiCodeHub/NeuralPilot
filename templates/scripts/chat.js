/**
 * NeuralPilot Chat Interface JavaScript
 * Handles all chat functionality including message sending, loading states, and UI interactions
 */

class ChatInterface {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.input = document.getElementById("input");
        this.chatbox = document.getElementById("chatbox");
        
        this.initializeEventListeners();
        this.addWelcomeMessage();
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Handle Enter key for sending messages
        this.input.addEventListener("keypress", (event) => {
            if (event.key === "Enter") {
                this.sendMessage();
            }
        });

        // Auto-resize input field
        this.input.addEventListener("input", (event) => {
            event.target.style.height = "auto";
            event.target.style.height = Math.min(event.target.scrollHeight, 120) + "px";
        });

        // Focus input on page load
        window.addEventListener("load", () => {
            this.input.focus();
        });
    }

    /**
     * Add welcome message to chat
     */
    addWelcomeMessage() {
        const welcomeMessage = `
            👋 Welcome to NeuralPilot! I'm your AI research assistant powered by GPT-4 and the latest machine learning papers from ArXiv. Ask me anything about ML, AI, deep learning, or related topics!
        `;
        this.addMessage(welcomeMessage, false);
    }

    /**
     * Add a message to the chat interface
     * @param {string} content - The message content
     * @param {boolean} isUser - Whether this is a user message
     * @returns {HTMLElement} The created message element
     */
    addMessage(content, isUser = false) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                ${content}
            </div>
        `;
        this.chatbox.appendChild(messageDiv);
        this.scrollToBottom();
        return messageDiv;
    }

    /**
     * Add a loading message to the chat
     * @returns {HTMLElement} The created loading message element
     */
    addLoadingMessage() {
        const loadingDiv = document.createElement("div");
        loadingDiv.className = "message loading-message";
        loadingDiv.innerHTML = `
            <div class="message-content">
                <span>NeuralPilot is thinking</span>
                <div class="loading-dots">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>
        `;
        this.chatbox.appendChild(loadingDiv);
        this.scrollToBottom();
        return loadingDiv;
    }

    /**
     * Replace loading message with bot response using smooth transition
     * @param {HTMLElement} loadingDiv - The loading message element
     * @param {string} response - The bot's response
     */
    replaceLoadingWithResponse(loadingDiv, response) {
        // Start fade out
        loadingDiv.classList.add('fade-out');
        
        setTimeout(() => {
            // Change content and start fade in
            loadingDiv.innerHTML = `
                <div class="message-content">
                    ${response}
                </div>
            `;
            loadingDiv.className = "message bot-message fade-in";
            this.scrollToBottom();
            
            // Remove animation classes after animation completes
            setTimeout(() => {
                loadingDiv.className = "message bot-message";
            }, 500);
            
        }, 300); // Shorter fade out for more responsive feel
    }

    /**
     * Scroll chat to the bottom
     */
    scrollToBottom() {
        this.chatbox.scrollTop = this.chatbox.scrollHeight;
    }

    /**
     * Send a message to the server
     */
    async sendMessage() {
        const userMsg = this.input.value.trim();
        if (!userMsg) return;

        // Clear input and add user message
        this.input.value = "";
        this.addMessage(userMsg, true);

        // Add loading message
        const loadingDiv = this.addLoadingMessage();

        try {
            const response = await this.makeApiRequest(userMsg);
            this.replaceLoadingWithResponse(loadingDiv, response);
        } catch (error) {
            console.error("Error sending message:", error);
            this.replaceLoadingWithResponse(loadingDiv, "Sorry, I encountered an error. Please try again.");
        }
    }

    /**
     * Make API request to the server
     * @param {string} message - The user's message
     * @returns {Promise<string>} The bot's response
     */
    async makeApiRequest(message) {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                message: message, 
                session_id: this.sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.response;
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get session ID from the template variable
    const sessionId = document.querySelector('meta[name="session-id"]')?.getAttribute('content');
    
    if (sessionId) {
        window.chatInterface = new ChatInterface(sessionId);
    } else {
        console.error('Session ID not found');
    }
});

// Global function for onclick handler (for backward compatibility)
function sendMessage() {
    if (window.chatInterface) {
        window.chatInterface.sendMessage();
    }
} 