# Chatbot Artifact Detection

A lightweight chatbot interface with artifact detection for rendering interactive charts from LLM responses.

## What You Need to Copy

### 1. Frontend Files

Copy these files to your project:

```
frontend/home/index.html          → Your frontend directory
frontend/home/js/chat.js          → Your frontend/js directory
```

**File Structure:**
```
your-project/
├── frontend/
│   ├── index.html
│   └── js/
│       └── chat.js
```

### 2. System Prompt

Copy this file for your LLM:

```
prompt.py                         → Your backend directory
```

This contains the system prompt with instructions for the LLM on how to format responses with artifacts.

## How It Works

### Frontend (index.html + chat.js)

The frontend automatically detects artifacts in LLM responses:

1. **Artifact Format**: LLM wraps chart data with markers:
   ```
   <<<ARTIFACT_START>>>
   { "type": "artifact", "artifact_type": "chart", ... }
   <<<ARTIFACT_END>>>
   ```

2. **Detection**: `chat.js` detects these markers and renders charts using Highcharts

3. **No Backend Changes Needed**: Just return the LLM response as-is

### Backend Integration

#### Step 1: Use the System Prompt

```python
from prompt import SYSTEM_PROMPT

# When calling your LLM
response = llm.chat([
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_message}
])

# Return the response directly to frontend
return response.content
```

#### Step 2: Create a Simple API Endpoint

**Example with FastAPI:**

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prompt import SYSTEM_PROMPT

app = FastAPI()

@app.post("/chat")
async def chat(message: str):
    # Call your LLM with the system prompt
    response = your_llm_client.chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ])

    # Return the response as-is
    # Frontend will detect and render artifacts automatically
    return JSONResponse({
        "response": response.content
    })
```

**Example with Flask:**

```python
from flask import Flask, request, jsonify
from prompt import SYSTEM_PROMPT

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message")

    # Call your LLM with the system prompt
    response = your_llm_client.chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ])

    # Return the response as-is
    return jsonify({
        "response": response.content
    })
```

#### Step 3: Update Frontend to Call Your API

In `chat.js`, replace the `mockLLMResponse` function:

```javascript
// Replace this function in chat.js
async function mockLLMResponse(userMessage) {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
    });

    const data = await response.json();
    return data.response;
}
```

That's it! The frontend will automatically detect and render any artifacts in the LLM response.

## Optional: Database Integration

If you want to enable the `duckdb_query` tool mentioned in the system prompt:

```python
import duckdb

def execute_duckdb_query(sql: str) -> str:
    conn = duckdb.connect('your_database.db')
    result = conn.execute(sql).fetchall()
    return str(result)

@app.post("/chat")
async def chat(message: str):
    response = your_llm_client.chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ])

    # If LLM wants to use the duckdb_query tool
    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call.name == "duckdb_query":
                sql = tool_call.parameters["sql"]
                result = execute_duckdb_query(sql)

                # Send result back to LLM
                response = your_llm_client.chat([
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                    {"role": "tool", "content": result}
                ])

    return JSONResponse({"response": response.content})
```

## Customization

### Change Colors

Edit the Tailwind config in `index.html`:

```javascript
colors: {
    primary: { DEFAULT: "#YOUR_COLOR" },
    accent: { DEFAULT: "#YOUR_COLOR" }
}
```

### Change Welcome Message

Edit the welcome section in `index.html` (around line 86-117)

### Add More Chart Types

The system supports: line, bar, column, pie, area, scatter

See `prompt.py` for examples of each chart type.

## Requirements

- **Frontend**: Modern browser with JavaScript enabled
- **Backend**: Any framework (FastAPI, Flask, Express, etc.)
- **LLM**: Any LLM that supports system prompts (OpenAI, Anthropic, etc.)
- **Optional**: DuckDB for database queries

## That's It!

Just copy the 3 files, connect your LLM, and you're ready to go. The frontend handles all artifact detection and rendering automatically.
