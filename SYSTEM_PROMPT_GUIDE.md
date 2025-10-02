# Risk Analyst Agent - System Prompt Guide

## Overview
The system prompt is designed for a Risk Analyst Agent that can query DuckDB databases and create interactive visualizations using Highcharts.

## Key Features

### 1. XML-Based Structure
The prompt uses XML tags for better LLM comprehension:
- `<role>` - Defines the agent's identity
- `<capabilities>` - Lists what the agent can do
- `<tools>` - Describes available tools
- `<workflow>` - Step-by-step process
- `<artifact_format>` - How to create visualizations
- `<important_rules>` - Critical guidelines
- `<example_conversations>` - Real-world examples

### 2. DuckDB Integration

**Tool: `duckdb_query`**
- **Parameter**: `sql` (string) - SQL query to execute
- **Returns**: Query results as a string
- **Purpose**: Retrieve data from database before visualization

**Example Usage:**
```python
# Agent calls tool
duckdb_query(sql="SELECT month, SUM(revenue) FROM sales GROUP BY month")

# Returns string result
# Agent parses result and creates chart
```

### 3. Artifact System

**Format:**
```
<<<ARTIFACT_START>>>
{
  "type": "artifact",
  "artifact_type": "chart",
  "title": "Chart Title",
  "description": "Description",
  "data": { /* Highcharts config */ }
}
<<<ARTIFACT_END>>>
```

**Supported Chart Types:**
- Line charts (trends over time)
- Bar charts (horizontal comparisons)
- Column charts (vertical comparisons)
- Pie charts (proportions)
- Area charts (cumulative values)

### 4. Workflow

**Step 1: Query Database**
```
User: "Show me sales trends"
Agent: Constructs SQL query
Agent: Calls duckdb_query tool
```

**Step 2: Process Results**
```
Agent: Parses string results
Agent: Transforms data for visualization
```

**Step 3: Create Visualization**
```
Agent: Generates artifact JSON
Agent: Wraps in markers
Agent: Returns with explanation
```

## Brand Styling

**Citi Bank Colors:**
- Primary: #003B70 (Citi Blue)
- Accent: #D9261C (Citi Red)

All charts should use these colors for consistency.

## Example Conversations

### Example 1: Data Visualization Request
```
User: "Show me sales data for the last 6 months"

Agent:
1. Calls duckdb_query with SQL
2. Parses results
3. Creates line chart artifact
4. Provides insights
```

### Example 2: Risk Analysis
```
User: "What are the top risk categories?"

Agent:
1. Queries risk_data table
2. Aggregates by category
3. Creates column chart
4. Highlights key findings
```

### Example 3: General Question
```
User: "Hello, how are you?"

Agent:
- Responds conversationally
- No database query needed
- No artifact created
```

## Integration with LLM

### Using the Prompt

```python
from prompt import SYSTEM_PROMPT

# Initialize LLM with system prompt
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_message}
]

response = llm.chat(messages)
```

### Tool Calling

When the LLM needs data:
```python
# LLM returns tool call
{
    "tool": "duckdb_query",
    "parameters": {
        "sql": "SELECT * FROM sales WHERE year = 2024"
    }
}

# Execute query
result = execute_duckdb_query(sql)

# Return result to LLM
{
    "tool_result": result_string
}

# LLM processes and creates artifact
```

## Best Practices

### For SQL Queries
1. Always validate SQL syntax
2. Use appropriate aggregations
3. Order results logically
4. Limit results when appropriate
5. Handle date formats correctly

### For Visualizations
1. Choose appropriate chart type for data
2. Use meaningful titles and labels
3. Apply brand colors
4. Disable Highcharts credits
5. Keep charts clean and readable

### For Responses
1. Explain what you're querying
2. Provide context with visualizations
3. Highlight key insights
4. Be professional and concise
5. Handle errors gracefully

## Error Handling

### Database Errors
```
If query fails:
- Explain the issue clearly
- Suggest alternative queries
- Don't create artifact
```

### Data Issues
```
If data is insufficient:
- Inform user about limitations
- Suggest what data is needed
- Provide partial results if possible
```

## Extending the System

### Adding New Chart Types
Update `<chart_examples>` section with:
- New chart type
- Use case
- Complete JSON example
- Styling guidelines

### Adding New Tools
Add to `<tools>` section:
- Tool name and description
- Parameters with types
- Usage guidelines
- Examples

### Modifying Workflow
Update `<workflow>` section:
- Add new steps
- Modify existing steps
- Provide clear instructions

## Testing

### Test Queries
```sql
-- Sales data
SELECT month, SUM(revenue) FROM sales GROUP BY month

-- Risk categories
SELECT category, COUNT(*) FROM risks GROUP BY category

-- Time series
SELECT date, value FROM metrics ORDER BY date
```

### Test Prompts
```
"Show me a chart of sales"
"What are the risk trends?"
"Visualize the data"
"Create a graph"
```

## Notes

- XML tags improve LLM understanding vs markdown
- Tool calling must be implemented by the backend
- Frontend automatically detects and renders artifacts
- Mock responses demonstrate expected format
- Real implementation requires actual DuckDB connection

