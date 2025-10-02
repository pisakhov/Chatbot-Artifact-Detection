const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');

let isWaitingForResponse = false;
let messages = [];

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + 'px';
}

messageInput.addEventListener('input', autoResizeTextarea);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (message && !isWaitingForResponse) {
            handleSubmit(e);
        }
    }
});

function clearWelcomeMessage() {
    const welcomeDiv = chatContainer.querySelector('.flex.items-center.justify-center');
    if (welcomeDiv) {
        chatContainer.innerHTML = '';
    }
}

function detectArtifact(content) {
    const artifactRegex = /<<<ARTIFACT_START>>>([\s\S]*?)<<<ARTIFACT_END>>>/;
    const match = content.match(artifactRegex);

    if (match) {
        const beforeArtifact = content.substring(0, match.index).trim();
        const artifactJson = match[1].trim();
        const afterArtifact = content.substring(match.index + match[0].length).trim();

        return {
            hasArtifact: true,
            beforeText: beforeArtifact,
            artifactData: artifactJson,
            afterText: afterArtifact
        };
    }

    return { hasArtifact: false };
}

function createChartElement(artifactData) {
    const chartContainer = document.createElement('div');
    chartContainer.className = 'w-full bg-white rounded-lg border border-border p-4 my-2';

    const chartId = 'chart-' + Date.now() + '-' + Math.random().toString(36).substring(2, 11);
    const chartDiv = document.createElement('div');
    chartDiv.id = chartId;
    chartDiv.className = 'w-full';
    chartDiv.style.minHeight = '400px';

    chartContainer.appendChild(chartDiv);

    setTimeout(() => {
        Highcharts.chart(chartId, artifactData.data);
    }, 100);

    return chartContainer;
}

function createMessageElement(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;

    const messageBubble = document.createElement('div');
    messageBubble.className = `max-w-[80%] rounded-lg px-4 py-3 ${
        isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-foreground'
    }`;

    const messageText = document.createElement('p');
    messageText.className = 'text-sm whitespace-pre-wrap break-words';
    messageText.textContent = content;

    messageBubble.appendChild(messageText);
    messageDiv.appendChild(messageBubble);

    return messageDiv;
}

function createArtifactMessage(content) {
    const artifact = detectArtifact(content);

    if (!artifact.hasArtifact) {
        return createMessageElement(content, false);
    }

    const containerDiv = document.createElement('div');
    containerDiv.className = 'flex justify-start w-full';

    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'max-w-[90%] space-y-2';

    if (artifact.beforeText) {
        const beforeDiv = document.createElement('div');
        beforeDiv.className = 'bg-muted text-foreground rounded-lg px-4 py-3';
        const beforeText = document.createElement('p');
        beforeText.className = 'text-sm whitespace-pre-wrap break-words';
        beforeText.textContent = artifact.beforeText;
        beforeDiv.appendChild(beforeText);
        contentWrapper.appendChild(beforeDiv);
    }

    const artifactData = JSON.parse(artifact.artifactData);
    const chartElement = createChartElement(artifactData);
    contentWrapper.appendChild(chartElement);

    if (artifact.afterText) {
        const afterDiv = document.createElement('div');
        afterDiv.className = 'bg-muted text-foreground rounded-lg px-4 py-3';
        const afterText = document.createElement('p');
        afterText.className = 'text-sm whitespace-pre-wrap break-words';
        afterText.textContent = artifact.afterText;
        afterDiv.appendChild(afterText);
        contentWrapper.appendChild(afterDiv);
    }

    containerDiv.appendChild(contentWrapper);
    return containerDiv;
}

function createLoadingElement() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'flex justify-start';
    loadingDiv.id = 'loadingIndicator';

    const loadingBubble = document.createElement('div');
    loadingBubble.className = 'bg-muted rounded-lg px-4 py-3';

    const dotsContainer = document.createElement('div');
    dotsContainer.className = 'flex gap-1';

    for (let i = 1; i <= 3; i++) {
        const dot = document.createElement('div');
        dot.className = `w-2 h-2 bg-foreground/60 rounded-full animate-pulse-dot-${i}`;
        dotsContainer.appendChild(dot);
    }

    loadingBubble.appendChild(dotsContainer);
    loadingDiv.appendChild(loadingBubble);

    return loadingDiv;
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function getLLMResponse() {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            messages: messages
        })
    });

    if (!response.ok) {
        throw new Error('Failed to get response from server');
    }

    const data = await response.json();
    return data.response;
}

async function handleSubmit(e) {
    e.preventDefault();

    const message = messageInput.value.trim();

    if (!message || isWaitingForResponse) return;

    clearWelcomeMessage();

    const userMessageElement = createMessageElement(message, true);
    chatContainer.appendChild(userMessageElement);
    scrollToBottom();

    messageInput.value = '';
    autoResizeTextarea();

    isWaitingForResponse = true;
    sendBtn.disabled = true;
    messageInput.disabled = true;

    const loadingElement = createLoadingElement();
    chatContainer.appendChild(loadingElement);
    scrollToBottom();

    try {
        messages.push({
            role: 'user',
            content: message
        });

        const response = await getLLMResponse();

        messages.push({
            role: 'assistant',
            content: response
        });

        loadingElement.remove();

        const assistantMessageElement = createArtifactMessage(response);
        chatContainer.appendChild(assistantMessageElement);
        scrollToBottom();
    } catch (error) {
        loadingElement.remove();

        const errorMessage = createMessageElement(
            'Sorry, I encountered an error. Please try again.',
            false
        );
        chatContainer.appendChild(errorMessage);
        scrollToBottom();

        console.error('Error getting LLM response:', error);
    }

    isWaitingForResponse = false;
    sendBtn.disabled = false;
    messageInput.disabled = false;
    messageInput.focus();
}

function handleNewChat() {
    messages = [];

    chatContainer.innerHTML = `
        <div class="flex items-center justify-center h-full">
            <div class="text-center space-y-4 max-w-2xl">
                <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                    <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                </div>
                <h2 class="text-3xl font-bold text-foreground">Risk Analyst Agent</h2>
                <p class="text-muted-foreground text-lg">Your AI-powered financial data analyst</p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-6 text-left">
                    <div class="bg-secondary/50 rounded-lg p-4 border border-border">
                        <div class="font-semibold text-sm text-foreground mb-1">📊 Data Visualization</div>
                        <div class="text-xs text-muted-foreground">Create interactive charts from database queries</div>
                    </div>
                    <div class="bg-secondary/50 rounded-lg p-4 border border-border">
                        <div class="font-semibold text-sm text-foreground mb-1">🔍 Risk Analysis</div>
                        <div class="text-xs text-muted-foreground">Analyze exposure and identify risk patterns</div>
                    </div>
                    <div class="bg-secondary/50 rounded-lg p-4 border border-border">
                        <div class="font-semibold text-sm text-foreground mb-1">💼 Financial Insights</div>
                        <div class="text-xs text-muted-foreground">Query sales, revenue, and performance data</div>
                    </div>
                    <div class="bg-secondary/50 rounded-lg p-4 border border-border">
                        <div class="font-semibold text-sm text-foreground mb-1">📈 Trend Detection</div>
                        <div class="text-xs text-muted-foreground">Identify patterns and growth opportunities</div>
                    </div>
                </div>
                <p class="text-xs text-muted-foreground mt-4">Try: "Show me risk analysis" or "Create a sales chart"</p>
            </div>
        </div>
    `;
    messageInput.value = '';
    autoResizeTextarea();
    messageInput.focus();
}

chatForm.addEventListener('submit', handleSubmit);
newChatBtn.addEventListener('click', handleNewChat);

messageInput.focus();

