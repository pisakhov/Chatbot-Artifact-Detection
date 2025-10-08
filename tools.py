from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path


KNOWLEDGE_DIR = "knowledge"
KNOWLEDGE_INDEX = os.path.join(KNOWLEDGE_DIR, "knowledge.json")


def ensure_knowledge_structure():
    """Ensure knowledge directory and index file exist"""
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    
    if not os.path.exists(KNOWLEDGE_INDEX):
        initial_data = {
            "metadata": {
                "created": datetime.utcnow().isoformat() + "Z",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "total_memories": 0,
                "next_id": 1
            },
            "memories": []
        }
        with open(KNOWLEDGE_INDEX, 'w') as f:
            json.dump(initial_data, f, indent=2)


def load_knowledge_index() -> Dict[str, Any]:
    """Load the knowledge index JSON"""
    ensure_knowledge_structure()
    with open(KNOWLEDGE_INDEX, 'r') as f:
        return json.load(f)


def save_knowledge_index(data: Dict[str, Any]):
    """Save the knowledge index JSON"""
    data["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
    with open(KNOWLEDGE_INDEX, 'w') as f:
        json.dump(data, f, indent=2)


@tool
def search_memory_index(
    query: str,
    category: Optional[str] = None,
    status: str = "active",
    limit: int = 5
) -> str:
    """
    Search the knowledge index (knowledge.json) for relevant memories using keyword matching.
    Returns metadata about matching memories including their file paths.
    
    Args:
        query: Keywords to search for (space-separated)
        category: Filter by category (user_profile, technical_knowledge, business_rules, etc.)
        status: Filter by status - 'active', 'retired', or 'all' (default: 'active')
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        JSON string with matching memory metadata including memory_id, file_path, category, tags, confidence, etc.
        
    Examples:
        search_memory_index("chart preferences")
        search_memory_index("database schema", category="technical_knowledge")
        search_memory_index("user settings", status="all", limit=3)
    """
    try:
        index_data = load_knowledge_index()
        memories = index_data.get("memories", [])
        
        if not memories:
            return json.dumps({
                "status": "success",
                "message": "No memories found in knowledge base",
                "results": []
            })
        
        # Filter by status
        if status != "all":
            memories = [m for m in memories if m.get("status") == status]
        
        # Filter by category
        if category:
            memories = [m for m in memories if m.get("category") == category]
        
        # Keyword matching and scoring
        query_keywords = query.lower().split()
        scored_memories = []
        
        for memory in memories:
            score = 0
            
            # Build searchable text
            searchable_parts = [
                memory.get("category", ""),
                " ".join(memory.get("tags", [])),
                memory.get("summary", "")
            ]
            searchable_text = " ".join(searchable_parts).lower()
            
            # Count keyword matches
            for keyword in query_keywords:
                if keyword in searchable_text:
                    score += searchable_text.count(keyword)
            
            # Boost by confidence
            confidence = memory.get("confidence", 0.5)
            score *= confidence
            
            # Boost by access count (popularity)
            access_count = memory.get("access_count", 0)
            score += access_count * 0.1
            
            # Boost by recency
            updated = memory.get("updated", memory.get("created", ""))
            if updated:
                try:
                    updated_date = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    days_old = (datetime.utcnow() - updated_date.replace(tzinfo=None)).days
                    recency_boost = max(0, 1 - (days_old / 365))
                    score += recency_boost * 0.5
                except:
                    pass
            
            if score > 0:
                scored_memories.append((score, memory))
        
        # Sort by score and limit
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        top_memories = scored_memories[:limit]
        
        # Increment access count for retrieved memories
        if top_memories:
            memory_ids = [m[1]["memory_id"] for m in top_memories]
            for memory in index_data["memories"]:
                if memory["memory_id"] in memory_ids:
                    memory["access_count"] = memory.get("access_count", 0) + 1
            save_knowledge_index(index_data)
        
        # Format results
        results = []
        for score, memory in top_memories:
            results.append({
                "memory_id": memory.get("memory_id"),
                "file_path": memory.get("file_path"),
                "category": memory.get("category"),
                "tags": memory.get("tags", []),
                "summary": memory.get("summary", ""),
                "confidence": memory.get("confidence", 0.5),
                "access_count": memory.get("access_count", 0),
                "status": memory.get("status", "active"),
                "created": memory.get("created", ""),
                "updated": memory.get("updated", ""),
                "relevance_score": round(score, 2)
            })
        
        return json.dumps({
            "status": "success",
            "message": f"Found {len(results)} relevant memories",
            "total_searched": len(memories),
            "results": results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error searching memory index: {str(e)}",
            "results": []
        })


@tool
def read_memory_file(memory_id: str) -> str:
    """
    Read the full content of a specific memory file.
    Use this after search_memory_index to get the complete memory content.
    
    Args:
        memory_id: The memory ID (e.g., 'MEMORY-001')
    
    Returns:
        The full content of the memory file
        
    Examples:
        read_memory_file("MEMORY-001")
    """
    try:
        index_data = load_knowledge_index()
        memories = index_data.get("memories", [])
        
        # Find memory by ID
        memory = next((m for m in memories if m.get("memory_id") == memory_id), None)
        
        if not memory:
            return f"Error: Memory {memory_id} not found in index"
        
        file_path = memory.get("file_path")
        if not file_path:
            return f"Error: No file path found for {memory_id}"
        
        full_path = os.path.join(KNOWLEDGE_DIR, file_path)
        
        if not os.path.exists(full_path):
            return f"Error: Memory file not found at {file_path}"
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Increment access count
        for mem in index_data["memories"]:
            if mem["memory_id"] == memory_id:
                mem["access_count"] = mem.get("access_count", 0) + 1
                break
        save_knowledge_index(index_data)
        
        return f"""Memory: {memory_id}
Category: {memory.get('category')}
Tags: {', '.join(memory.get('tags', []))}
Status: {memory.get('status')}
Confidence: {memory.get('confidence')}
Created: {memory.get('created')}
Updated: {memory.get('updated')}

Content:
{content}"""
        
    except Exception as e:
        return f"Error reading memory file: {str(e)}"


@tool
def manage_memory(
    action: str,
    content: str = "",
    memory_id: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    summary: Optional[str] = None,
    confidence: Optional[float] = None
) -> str:
    """
    Create, update, or retire memories. This manages both the index and memory files.
    
    Args:
        action: 'create' | 'update' | 'retire' | 'consolidate'
        content: The full memory content (required for create/update)
        memory_id: Memory ID like 'MEMORY-001' (required for update/retire/consolidate)
        category: Category name (required for create)
        tags: Comma-separated tags like "preferences, charts, user"
        summary: Brief one-line summary of the memory (required for create)
        confidence: Confidence score 0.0-1.0 (optional, default: 0.8 for create)
    
    Returns:
        Confirmation message with memory ID and action taken
        
    Examples:
        manage_memory(action="create", content="User prefers dark mode UI...", category="user_profile", tags="preferences, ui", summary="User UI preferences")
        manage_memory(action="update", memory_id="MEMORY-001", content="Updated content...")
        manage_memory(action="retire", memory_id="MEMORY-003")
        manage_memory(action="consolidate", memory_id="MEMORY-001,MEMORY-005", content="Merged content...", summary="Consolidated preferences")
    """
    try:
        if action == "create":
            return _create_memory(content, category, tags, summary, confidence)
        elif action == "update":
            return _update_memory(memory_id, content, tags, summary, confidence)
        elif action == "retire":
            return _retire_memory(memory_id)
        elif action == "consolidate":
            return _consolidate_memories(memory_id, content, tags, summary, confidence)
        else:
            return f"Error: Unknown action '{action}'. Use: create, update, retire, or consolidate"
    except Exception as e:
        return f"Error in manage_memory: {str(e)}"


def _create_memory(content: str, category: str, tags: Optional[str], summary: Optional[str], confidence: Optional[float]) -> str:
    """Create a new memory"""
    if not content:
        return "Error: content is required for create action"
    if not category:
        return "Error: category is required for create action"
    if not summary:
        return "Error: summary is required for create action"
    
    index_data = load_knowledge_index()
    
    # Check for duplicates
    query_keywords = set(content.lower().split()[:20])
    for memory in index_data["memories"]:
        if memory.get("status") != "active":
            continue
        
        existing_summary = memory.get("summary", "").lower()
        existing_keywords = set(existing_summary.split())
        
        overlap = len(query_keywords & existing_keywords)
        similarity = overlap / len(query_keywords) if query_keywords else 0
        
        if similarity > 0.6:
            return f"Warning: Similar memory found: {memory['memory_id']} - '{memory.get('summary')}'. Consider updating it or use consolidate action."
    
    # Generate new ID
    next_id = index_data["metadata"]["next_id"]
    memory_id = f"MEMORY-{str(next_id).zfill(3)}"
    file_name = f"{memory_id.lower()}.md"
    file_path = file_name
    
    # Create memory file
    full_path = os.path.join(KNOWLEDGE_DIR, file_path)
    with open(full_path, 'w') as f:
        f.write(content)
    
    # Create index entry
    now = datetime.utcnow().isoformat() + "Z"
    tags_list = [t.strip() for t in tags.split(",")] if tags else []
    confidence_val = confidence if confidence is not None else 0.8
    
    memory_entry = {
        "memory_id": memory_id,
        "file_path": file_path,
        "category": category,
        "tags": tags_list,
        "summary": summary,
        "confidence": confidence_val,
        "access_count": 0,
        "status": "active",
        "created": now,
        "updated": now
    }
    
    index_data["memories"].append(memory_entry)
    index_data["metadata"]["next_id"] = next_id + 1
    index_data["metadata"]["total_memories"] = len([m for m in index_data["memories"] if m["status"] == "active"])
    
    save_knowledge_index(index_data)
    
    return f"✅ Created {memory_id} in category '{category}' (file: {file_path})"


def _update_memory(memory_id: str, content: Optional[str], tags: Optional[str], summary: Optional[str], confidence: Optional[float]) -> str:
    """Update an existing memory"""
    if not memory_id:
        return "Error: memory_id is required for update action"
    
    index_data = load_knowledge_index()
    
    # Find memory
    memory = next((m for m in index_data["memories"] if m["memory_id"] == memory_id), None)
    if not memory:
        return f"Error: Memory {memory_id} not found"
    
    # Update file content if provided
    if content:
        full_path = os.path.join(KNOWLEDGE_DIR, memory["file_path"])
        with open(full_path, 'w') as f:
            f.write(content)
    
    # Update index metadata
    now = datetime.utcnow().isoformat() + "Z"
    memory["updated"] = now
    
    if tags:
        memory["tags"] = [t.strip() for t in tags.split(",")]
    
    if summary:
        memory["summary"] = summary
    
    if confidence is not None:
        memory["confidence"] = confidence
    
    save_knowledge_index(index_data)
    
    return f"✅ Updated {memory_id}"


def _retire_memory(memory_id: str) -> str:
    """Retire a memory"""
    if not memory_id:
        return "Error: memory_id is required for retire action"
    
    index_data = load_knowledge_index()
    
    # Find memory
    memory = next((m for m in index_data["memories"] if m["memory_id"] == memory_id), None)
    if not memory:
        return f"Error: Memory {memory_id} not found"
    
    # Update status
    memory["status"] = "retired"
    memory["confidence"] = 0.3
    memory["updated"] = datetime.utcnow().isoformat() + "Z"
    
    index_data["metadata"]["total_memories"] = len([m for m in index_data["memories"] if m["status"] == "active"])
    
    save_knowledge_index(index_data)
    
    return f"✅ Retired {memory_id}"


def _consolidate_memories(memory_ids_str: str, content: str, tags: Optional[str], summary: Optional[str], confidence: Optional[float]) -> str:
    """Consolidate multiple memories into one"""
    if not memory_ids_str:
        return "Error: memory_id is required for consolidate action (comma-separated list)"
    if not content:
        return "Error: content is required for consolidate action"
    if not summary:
        return "Error: summary is required for consolidate action"
    
    memory_ids = [m.strip() for m in memory_ids_str.split(",")]
    
    if len(memory_ids) < 2:
        return "Error: Consolidate requires at least 2 memory IDs (comma-separated)"
    
    index_data = load_knowledge_index()
    
    # Find all memories
    to_merge = [m for m in index_data["memories"] if m["memory_id"] in memory_ids]
    
    if len(to_merge) != len(memory_ids):
        found_ids = [m["memory_id"] for m in to_merge]
        missing = set(memory_ids) - set(found_ids)
        return f"Error: Some memory IDs not found: {missing}"
    
    # Get highest confidence and most common category
    max_confidence = max(m["confidence"] for m in to_merge)
    categories = [m["category"] for m in to_merge]
    most_common_category = max(set(categories), key=categories.count)
    
    # Combine tags
    all_tags = []
    for m in to_merge:
        all_tags.extend(m.get("tags", []))
    unique_tags = list(set(all_tags))
    
    if tags:
        unique_tags.extend([t.strip() for t in tags.split(",")])
        unique_tags = list(set(unique_tags))
    
    # Create new consolidated memory
    final_confidence = confidence if confidence is not None else max_confidence
    result = _create_memory(
        content=content,
        category=most_common_category,
        tags=", ".join(unique_tags),
        summary=summary,
        confidence=final_confidence
    )
    
    # Retire old memories
    for memory_id in memory_ids:
        _retire_memory(memory_id)
    
    return f"✅ Consolidated {', '.join(memory_ids)} into new memory. {result}"

