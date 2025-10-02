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

## Short-Term Memory (Conversation History)

The frontend automatically tracks conversation history in a **messages array** (LangChain format):

```javascript
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Show me sales data"}
]
```

Your backend receives this array with each request - just convert it to your LLM's format!

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

**Example with LangChain:**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from prompt import SYSTEM_PROMPT

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/chat")
async def chat(request: ChatRequest):
    llm = ChatOpenAI(model="gpt-4")

    # Build messages
    langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for msg in request.messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    response = llm.invoke(langchain_messages)
    return {"response": response.content}
```

See `backend_langchain.py` for complete examples with tools, streaming, and more!

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
