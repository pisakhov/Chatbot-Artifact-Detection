"""
Backend Example using LangChain with Messages Array

The frontend sends a messages array in LangChain format:
[
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"},
    {"role": "user", "content": "Show me data"}
]
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict
from prompt import SYSTEM_PROMPT

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend")


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("home/index.html", {"request": request})


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint using LangChain messages format
    
    Frontend sends:
    {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"},
            {"role": "user", "content": "Show me sales data"}
        ]
    }
    """
    
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7
    )
    
    # Build messages with system prompt
    langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    
    # Convert frontend messages to LangChain format
    for msg in request.messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
    
    # Get response
    response = llm.invoke(langchain_messages)
    
    return JSONResponse({
        "response": response.content
    })


# Example with LangChain Agent and Tools
@app.post("/chat-with-tools")
async def chat_with_tools(request: ChatRequest):
    """
    Example using LangChain Agent with DuckDB tool
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.tools import tool
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    import duckdb
    
    @tool
    def duckdb_query(sql: str) -> str:
        """Executes SQL queries against the DuckDB database and returns results as a string"""
        conn = duckdb.connect('database.db')
        result = conn.execute(sql).fetchall()
        return str(result)
    
    tools = [duckdb_query]
    
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Create prompt with system message and chat history
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Convert messages to LangChain format for chat history
    chat_history = []
    for msg in request.messages[:-1]:  # All except last message
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))
    
    # Get last user message
    last_message = request.messages[-1]["content"] if request.messages else ""
    
    # Execute agent
    result = agent_executor.invoke({
        "input": last_message,
        "chat_history": chat_history
    })
    
    return JSONResponse({
        "response": result["output"]
    })


# Example with Anthropic Claude via LangChain
@app.post("/chat-claude")
async def chat_claude(request: ChatRequest):
    """
    Example using Anthropic Claude via LangChain
    """
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7
    )
    
    # Build messages
    langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    
    for msg in request.messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
    
    # Get response
    response = llm.invoke(langchain_messages)
    
    return JSONResponse({
        "response": response.content
    })


# Example with streaming response
@app.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming response for real-time output
    """
    from fastapi.responses import StreamingResponse
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        streaming=True
    )
    
    # Build messages
    langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    
    for msg in request.messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
    
    async def generate():
        async for chunk in llm.astream(langchain_messages):
            if chunk.content:
                yield chunk.content
    
    return StreamingResponse(generate(), media_type="text/plain")


# Example with memory using LangChain's built-in memory
@app.post("/chat-with-memory")
async def chat_with_memory(request: ChatRequest, session_id: str = "default"):
    """
    Example using LangChain's ConversationBufferMemory
    """
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain
    
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # In production, store memory per session_id (e.g., in Redis)
    memory = ConversationBufferMemory()
    
    # Load previous messages into memory
    for msg in request.messages[:-1]:
        if msg["role"] == "user":
            memory.chat_memory.add_user_message(msg["content"])
        elif msg["role"] == "assistant":
            memory.chat_memory.add_ai_message(msg["content"])
    
    # Create conversation chain
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    
    # Get last user message
    last_message = request.messages[-1]["content"] if request.messages else ""
    
    # Get response
    response = conversation.predict(input=last_message)
    
    return JSONResponse({
        "response": response
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

