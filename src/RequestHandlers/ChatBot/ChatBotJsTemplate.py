chat_bot_js_template = """
document.addEventListener("DOMContentLoaded", async function () {
    console.log("Ajentify Chatbot Script Loaded");

    if (window.AjentifyChatbot) return;
    window.AjentifyChatbot = true;

    console.log("Initializing chatbot...");

    let contextId = null;
    let agentId = "<%agent_id%>";
    let agentSpeaksFirst = <%agent_speaks_first%>;

    let headerTitle = "<%header_title%>";
    let chatButtonTitle = "<%chat_button_title%>";

    // Define color variables
    let primaryColor = "<%primary_color%>";
    let botMessageColor = "<%bot_message_color%>";
    let botTextColor = "<%bot_text_color%>";
    let userMessageColor = "<%user_message_color%>";
    let userTextColor = "<%user_text_color%>";
    let chatBackgroundColor = "<%chat_background_color%>";
    let chatBorderColor = "<%chat_border_color%>";
    let inputTextColor = "<%input_text_color%>";
    let inputBackgroundColor = "<%input_background_color%>";

    const style = document.createElement('style');
    style.innerHTML = `
    #chat-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${primaryColor};
        color: ${userTextColor};
        padding: 10px 15px;
        border-radius: 25px;
        cursor: pointer;
        box-shadow: 0 4px 6px ${chatBorderColor};
        font-size: 16px;
        font-family: Arial, sans-serif;
        z-index: 1000;
    }
    #chat-container {
        position: fixed;
        bottom: 70px;
        right: 20px;
        width: 300px;
        height: 400px;
        background: ${chatBackgroundColor};
        box-shadow: 0 4px 10px ${chatBorderColor};
        border-radius: 10px;
        display: none;
        flex-direction: column;
        overflow: hidden;
        z-index: 1000;
    }
    #chat-header {
        background: ${primaryColor};
        color: ${userTextColor};
        padding: 10px;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
    }
    #chat-messages {
        flex: 1;
        padding: 10px;
        overflow-y: auto;
        font-family: Arial, sans-serif;
        display: flex;
        flex-direction: column;
        scroll-behavior: smooth;
    }
    .message {
        padding: 8px 12px;
        margin: 5px;
        border-radius: 16px;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 16px;
    }
    .bot-message {
        background: ${botMessageColor};
        color: ${botTextColor};
        align-self: flex-start;
    }
    .user-message {
        background: ${userMessageColor};
        color: ${userTextColor};
        align-self: flex-end;
    }
    .typing-indicator {
        padding: 8px 12px;
        margin: 5px;
        border-radius: 16px;
        max-width: 70%;
        word-wrap: break-word;
        background: ${botMessageColor};
        color: ${botTextColor};
        align-self: flex-start;
        display: flex;
        gap: 4px;
        align-items: center;
        justify-content: center;
    }
    .typing-indicator span {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: ${botTextColor};
        border-radius: 50%;
        animation: typing 1.5s infinite ease-in-out;
    }
    @keyframes typing {
        0% { opacity: 0.3; }
        50% { opacity: 1; }
        100% { opacity: 0.3; }
    }
    .typing-indicator span:nth-child(1) { animation-delay: 0s; }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    #chat-input {
        width: 100%;
        border: none;
        padding: 10px;
        box-sizing: border-box;
        resize: none;
        min-height: 40px;
        max-height: 120px;
        overflow-y: auto;
        font-family: Arial, sans-serif;
        font-size: 16px;
        color: ${inputTextColor};
        background: ${inputBackgroundColor};
    }
`;
    document.head.appendChild(style);

    const button = document.createElement('div');
    button.id = 'chat-button';
    button.innerText = chatButtonTitle;
    document.body.appendChild(button);

    const chatContainer = document.createElement('div');
    chatContainer.id = 'chat-container';
    chatContainer.style.display = "none";
    chatContainer.innerHTML = `
    <div id="chat-header">${headerTitle}</div>
    <div id="chat-messages"></div>
    <textarea id="chat-input" placeholder="Type a message..."></textarea>
`;
    document.body.appendChild(chatContainer);

    const chatMessages = document.getElementById('chat-messages');
    const input = document.getElementById('chat-input');

    function scrollToBottom() {
        chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: "smooth" });
    }

    button.onclick = () => {
        chatContainer.style.display = chatContainer.style.display === 'none' ? 'flex' : 'none';
        if (agentSpeaksFirst && !contextId) createContext();
    };

    document.addEventListener('click', (event) => {
        if (chatContainer.style.display === 'flex' && !chatContainer.contains(event.target) && event.target !== button) {
            chatContainer.style.display = 'none';
        }
    });

    input.addEventListener("input", function () {
        this.style.height = "auto";
        this.style.height = Math.min(this.scrollHeight, 120) + "px";
    });

    input.addEventListener('keydown', async function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim()) {
                const userMessage = this.value;
                this.value = '';
                this.style.height = "60px";
                appendMessage('You', userMessage, 'user-message');
                if (!contextId) await createContext();
                await sendMessage(userMessage);
            }
        }
    });

    async function createContext() {
        appendTypingIndicator();
        const response = await fetch('https://api.ajentify.com/context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_id: agentId })
        });
        const data = await response.json();
        contextId = data.context_id;
        removeTypingIndicator();
        if (agentSpeaksFirst) appendMessage('Bot', data.messages[0].message, 'bot-message');
    }

    async function sendMessage(message) {
        appendTypingIndicator();
        const response = await fetch('https://api.ajentify.com/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ context_id: contextId, message })
        });
        const data = await response.json();
        removeTypingIndicator();
        appendMessage('Bot', data.response, 'bot-message');
    }

    function appendMessage(sender, message, className) {
        const msgDiv = document.createElement('div');
        msgDiv.innerText = message;
        msgDiv.classList.add("message", className);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        scrollToBottom();
    }

    function appendTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.classList.add('typing-indicator');
        typingDiv.innerHTML = `<span></span><span></span><span></span>`;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) typingDiv.remove();
    }
});
"""