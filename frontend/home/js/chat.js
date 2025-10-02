const chatContainer = document.getElementById('chatContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');

let isWaitingForResponse = false;

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

async function mockLLMResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.includes('risk')) {
        await new Promise(resolve => setTimeout(resolve, 2000));

        return `Let me analyze the risk data from our database.

[Querying database with: SELECT risk_category, SUM(exposure_amount) as total_exposure FROM risk_data GROUP BY risk_category ORDER BY total_exposure DESC]

Here's the risk exposure breakdown:

<<<ARTIFACT_START>>>
{
  "type": "artifact",
  "artifact_type": "chart",
  "title": "Risk Exposure by Category",
  "description": "Total exposure amount across different risk categories",
  "data": {
    "chart": {
      "type": "column"
    },
    "title": {
      "text": "Risk Exposure Analysis"
    },
    "xAxis": {
      "categories": ["Credit Risk", "Market Risk", "Operational", "Liquidity", "Compliance"]
    },
    "yAxis": {
      "title": {
        "text": "Exposure ($M)"
      }
    },
    "series": [{
      "name": "Exposure Amount",
      "data": [450, 380, 290, 210, 180],
      "color": "#D9261C"
    }],
    "credits": {
      "enabled": false
    }
  }
}
<<<ARTIFACT_END>>>

Key findings: Credit Risk shows the highest exposure at $450M, representing 29% of total risk. I recommend prioritizing mitigation strategies for Credit and Market Risk categories.`;
    }

    if (lowerMessage.includes('chart') || lowerMessage.includes('graph') || lowerMessage.includes('visualize') || lowerMessage.includes('sales') || lowerMessage.includes('data')) {
        await new Promise(resolve => setTimeout(resolve, 2000));

        return `Let me query the sales data for you.

[Querying database with: SELECT month, SUM(revenue) as total_revenue FROM sales WHERE year = 2024 GROUP BY month ORDER BY month]

Here's the sales performance visualization:

<<<ARTIFACT_START>>>
{
  "type": "artifact",
  "artifact_type": "chart",
  "title": "Sales Performance 2024",
  "description": "Monthly sales revenue for the current year",
  "data": {
    "chart": {
      "type": "line"
    },
    "title": {
      "text": "Monthly Sales Performance"
    },
    "xAxis": {
      "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    },
    "yAxis": {
      "title": {
        "text": "Revenue ($)"
      }
    },
    "series": [{
      "name": "2024 Sales",
      "data": [45000, 52000, 48000, 61000, 58000, 67000],
      "color": "#003B70"
    }],
    "credits": {
      "enabled": false
    }
  }
}
<<<ARTIFACT_END>>>

Analysis: The data shows steady growth with a total revenue of $331,000 over the 6-month period. Notable spike in April (+27% MoM).`;
    }

    const responses = [
        "I'm your Risk Analyst Agent. I can help you analyze financial data, assess risks, and create visualizations. Try asking me about sales data, risk analysis, or request a chart!",
        "I understand. As a Risk Analyst Agent, I can query our database and provide insights. What specific data would you like to analyze?",
        "That's an interesting question. I specialize in financial and risk analysis. Would you like me to pull some data from the database to help answer that?",
        "I'm here to help with data analysis and risk assessment. Feel free to ask me to visualize any financial metrics or risk indicators.",
        "As your Risk Analyst Agent, I can access the database and create visualizations. What would you like to explore today?"
    ];

    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

    return responses[Math.floor(Math.random() * responses.length)];
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

    const response = await mockLLMResponse(message);

    loadingElement.remove();

    const assistantMessageElement = createArtifactMessage(response);
    chatContainer.appendChild(assistantMessageElement);
    scrollToBottom();

    isWaitingForResponse = false;
    sendBtn.disabled = false;
    messageInput.disabled = false;
    messageInput.focus();
}

function handleNewChat() {
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

