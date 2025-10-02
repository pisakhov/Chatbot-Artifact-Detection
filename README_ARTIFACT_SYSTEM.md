# Risk Analyst Agent - Artifact Detection System

## Overview
A complete implementation of an AI-powered Risk Analyst Agent with database querying capabilities and interactive chart visualization using Highcharts.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                    (Citi Bank Styled Chat)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (chat.js)                      │
│  • Artifact Detection (<<<ARTIFACT_START/END>>>)            │
│  • Chart Rendering (Highcharts)                             │
│  • Message Handling                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  • LLM Integration                                           │
│  • Tool Calling (duckdb_query)                              │
│  • Response Formatting                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DuckDB Database                           │
│  • Financial Data                                            │
│  • Risk Metrics                                              │
│  • Transaction Records                                       │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. System Prompt (`prompt.py`)

**Purpose**: Instructs the LLM on how to act as a Risk Analyst Agent

**Key Features**:
- XML-based structure for better LLM comprehension
- Defines `duckdb_query` tool usage
- Provides artifact format specifications
- Includes multiple chart type examples
- Contains example conversations

**Usage**:
```python
from prompt import SYSTEM_PROMPT

# Use in LLM initialization
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_query}
]
```

### 2. Frontend Detection (`frontend/home/js/chat.js`)

**Key Functions**:

#### `detectArtifact(content)`
Detects artifact markers in LLM response
```javascript
const artifact = detectArtifact(response);
// Returns: { hasArtifact, beforeText, artifactData, afterText }
```

#### `createChartElement(artifactData)`
Creates and renders Highcharts visualization
```javascript
const chart = createChartElement(artifactData);
// Returns: DOM element with rendered chart
```

#### `createArtifactMessage(content)`
Main function to render complete message with artifacts
```javascript
const message = createArtifactMessage(response);
// Returns: Complete message element with text + chart
```

#### `mockLLMResponse(userMessage)`
Simulates LLM responses (replace with real LLM API)
```javascript
const response = await mockLLMResponse(userMessage);
// Returns: Text response or artifact format
```

### 3. HTML Integration (`frontend/home/index.html`)

**Highcharts CDN**:
```html
<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="https://code.highcharts.com/modules/export-data.js"></script>
```

**Styling**: Citi Bank brand colors (#003B70, #D9261C)

## Artifact Format

### Structure
```
<<<ARTIFACT_START>>>
{
  "type": "artifact",
  "artifact_type": "chart",
  "title": "Chart Title",
  "description": "Brief description",
  "data": {
    // Highcharts configuration object
  }
}
<<<ARTIFACT_END>>>
```

### Example Response
```
Let me query the database for sales data.

[Querying: SELECT month, revenue FROM sales]

Here's the visualization:

<<<ARTIFACT_START>>>
{
  "type": "artifact",
  "artifact_type": "chart",
  "title": "Sales Trend",
  "description": "Monthly sales for 2024",
  "data": {
    "chart": { "type": "line" },
    "title": { "text": "Monthly Sales" },
    "xAxis": { "categories": ["Jan", "Feb", "Mar"] },
    "yAxis": { "title": { "text": "Revenue ($)" } },
    "series": [{
      "name": "Sales",
      "data": [45000, 52000, 48000],
      "color": "#003B70"
    }],
    "credits": { "enabled": false }
  }
}
<<<ARTIFACT_END>>>

The data shows positive growth trend.
```

## Workflow

### User Request → Database Query → Visualization

**Step 1: User asks for data**
```
User: "Show me risk exposure by category"
```

**Step 2: Agent queries database**
```python
# LLM decides to use tool
tool_call = {
    "tool": "duckdb_query",
    "parameters": {
        "sql": "SELECT category, SUM(exposure) FROM risks GROUP BY category"
    }
}

# Backend executes query
result = execute_duckdb_query(sql)
# Returns: "Credit Risk,450\nMarket Risk,380\n..."
```

**Step 3: Agent processes results**
```python
# LLM receives query results
# Parses data
# Formats for Highcharts
```

**Step 4: Agent creates artifact**
```
Agent returns response with artifact markers
Frontend detects markers
Renders chart with Highcharts
```

## Testing

### Current Mock Implementation

**Test Keywords**:
- "risk" → Shows risk exposure column chart
- "sales", "chart", "graph", "visualize", "data" → Shows sales line chart
- Other queries → General Risk Analyst responses

### Test Commands

```bash
# Start server
source venv/bin/activate
python main.py

# Run browser test
python test_browser.py
```

### Manual Testing

1. Open http://localhost:8000
2. Try these prompts:
   - "Show me risk analysis"
   - "Create a sales chart"
   - "Visualize the data"
   - "What are the risk categories?"

## Integration with Real LLM

### Backend Implementation

```python
from prompt import SYSTEM_PROMPT
import duckdb

def execute_duckdb_query(sql: str) -> str:
    conn = duckdb.connect('database.db')
    result = conn.execute(sql).fetchall()
    return str(result)

def chat_with_agent(user_message: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    response = llm.chat(messages)
    
    # Check if LLM wants to use tool
    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call.name == "duckdb_query":
                sql = tool_call.parameters["sql"]
                result = execute_duckdb_query(sql)
                
                # Send result back to LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
                
                # Get final response
                response = llm.chat(messages)
    
    return response.content
```

### FastAPI Endpoint

```python
@app.post("/chat")
async def chat(message: str):
    response = chat_with_agent(message)
    return {"response": response}
```

### Frontend Integration

```javascript
async function mockLLMResponse(userMessage) {
    // Replace with real API call
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
    });
    
    const data = await response.json();
    return data.response;
}
```

## Chart Types Supported

### Line Chart
**Use Case**: Trends over time
**Example**: Sales trends, risk scores over time

### Column Chart
**Use Case**: Vertical comparisons
**Example**: Risk exposure by category

### Bar Chart
**Use Case**: Horizontal comparisons
**Example**: Product performance comparison

### Pie Chart
**Use Case**: Proportions and percentages
**Example**: Market share, portfolio allocation

### Area Chart
**Use Case**: Cumulative values
**Example**: Portfolio growth, cumulative revenue

## Styling Guidelines

### Citi Bank Brand Colors
- **Primary**: #003B70 (Citi Blue)
- **Accent**: #D9261C (Citi Red)

### Chart Configuration
```json
{
  "series": [{
    "color": "#003B70"
  }],
  "credits": {
    "enabled": false
  }
}
```

## Files Structure

```
.
├── prompt.py                          # System prompt with XML tags
├── main.py                            # FastAPI server
├── frontend/
│   ├── base.html                      # Base template
│   └── home/
│       ├── index.html                 # Main chat interface
│       └── js/
│           └── chat.js                # Artifact detection & rendering
├── ARTIFACT_IMPLEMENTATION.md         # Implementation details
├── SYSTEM_PROMPT_GUIDE.md            # Prompt usage guide
└── README_ARTIFACT_SYSTEM.md         # This file
```

## Next Steps

1. **Connect Real LLM**: Replace mock with actual LLM API (OpenAI, Anthropic, etc.)
2. **Add DuckDB**: Set up actual database with financial data
3. **Implement Tool Calling**: Add backend logic for duckdb_query tool
4. **Add More Chart Types**: Scatter, heatmap, gauge charts
5. **Error Handling**: Graceful handling of SQL errors, invalid data
6. **Authentication**: Add user authentication for production
7. **Data Validation**: Validate SQL queries before execution
8. **Caching**: Cache frequent queries for performance

## Security Considerations

- **SQL Injection**: Validate and sanitize all SQL queries
- **Query Limits**: Implement row limits and timeouts
- **Access Control**: Restrict database access by user role
- **Data Privacy**: Ensure sensitive data is properly masked
- **Rate Limiting**: Prevent abuse of query endpoint

