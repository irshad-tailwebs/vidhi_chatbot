const sendButton = document.getElementById('send-button');
const userQueryInput = document.getElementById('user-query');
const chatContainer = document.getElementById('chat-container');
const errorMessageElement = document.getElementById('error-message');

function displayMessage(message, isBot = true) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add('mb-4');
    messageElement.classList.add('max-w-[80%]');
    messageElement.classList.add(isBot ? 'mr-auto' : 'ml-auto');

    if (isBot && message.includes('--------------------------------------------------')) {
        const responses = message.split('--------------------------------------------------');
        
        responses.forEach((response) => {
            if (response.trim()) {
                const responseContainer = document.createElement('div');
                responseContainer.classList.add('bg-gray-100');
                responseContainer.classList.add('rounded-lg');
                responseContainer.classList.add('p-4');
                responseContainer.classList.add('shadow-sm');

                const formattedResponse = formatBotResponse(response.trim());
                responseContainer.innerHTML = formattedResponse;

                messageElement.appendChild(responseContainer);
            }
        });
    } else {
        const messageContent = document.createElement('div');
        messageContent.classList.add('p-3');
        messageContent.classList.add('rounded-lg');
        if (isBot) {
            messageContent.classList.add('bg-gray-100');
        } else {
            messageContent.classList.add('bg-blue-500');
            messageContent.classList.add('text-white');
        }
        messageContent.textContent = message;
        messageElement.appendChild(messageContent);
    }

    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function formatBotResponse(response) {
    const sections = response.split('\n\n');
    let html = '<div class="flex flex-col gap-3">';

    sections.forEach((section) => {
        if (section.trim()) {
            if (section.includes("consequences may include")) {
                html += `<div class="bg-blue-50 p-3 border-l-4 border-blue-500 rounded">${section}</div>`;
            } else if (section.includes("⚖️")) {
                html += `<div class="text-gray-600 italic border-t border-gray-200 pt-3 mt-3">${section}</div>`;
            } else {
                html += `<div class="text-gray-800">${section}</div>`;
            }
        }
    });

    html += '</div>';
    return html;
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendQuery();
    }
}

async function sendQuery() {
    const userQuery = userQueryInput.value.trim();
    if (!userQuery) return;

    errorMessageElement.textContent = '';
    displayMessage(userQuery, false);
    userQueryInput.value = '';

    try {
        const response = await axios.post('/ask', {
            query: userQuery
        }, {
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 10000
        });

        const botResponse = response.data.response || "Sorry, no response found.";
        displayMessage(botResponse);

    } catch (error) {
        console.error("Detailed error:", error);
        
        let errorMessage = "An error occurred. ";
        if (error.response) {
            errorMessage += `Server responded with ${error.response.status}: ${error.response.data.error || ''}`;
        } else if (error.request) {
            errorMessage += "No response received from the server. Check your connection.";
        } else {
            errorMessage += error.message;
        }

        errorMessageElement.textContent = errorMessage;
        displayMessage("Sorry, there was a problem connecting to the legal chatbot.", true);
    }
}

// Initial welcome message
document.addEventListener('DOMContentLoaded', () => {
    displayMessage("Hi! I'm a legal assistant. Ask me about laws and regulations.");
}); 