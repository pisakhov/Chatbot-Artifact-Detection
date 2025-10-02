# Artifact Detection & Rendering Implementation

## Overview
This implementation allows the chat interface to detect and render data visualizations (charts) as artifacts using Highcharts.

## Architecture

### 1. System Prompt (`prompt.py`)
Contains instructions for the LLM on how to format responses with artifacts.

**Key Features:**
- Defines artifact format with `<<<ARTIFACT_START>>>` and `<<<ARTIFACT_END>>>` markers
- Provides Highcharts configuration examples (line, bar, pie charts)
- Includes example conversations
- Clear rules for when to use artifacts vs regular text

**Usage:**
```python
from prompt import SYSTEM_PROMPT

# Use SYSTEM_PROMPT when initializing your LLM
```

### 2. Frontend Detection (`chat.js`)

**Functions:**

#### `detectArtifact(content)`
- Parses message content for artifact markers
- Extracts text before, artifact JSON, and text after
- Returns object with detection results

#### `createChartElement(artifactData)`
- Creates DOM element for chart container
- Generates unique chart ID
- Initializes Highcharts with provided configuration
- Applies Citi bank styling

#### `createArtifactMessage(content)`
- Main function to render messages with artifacts
- Handles text before/after artifact
- Renders chart in between text sections
- Returns complete message element

#### `mockLLMResponse(userMessage)`
- Simulates LLM responses
- Detects keywords (chart, graph, visualize, sales, data)
- Returns artifact format for visualization requests
- Returns regular text for other queries

### 3. HTML Integration (`index.html`)

**Added CDN Scripts:**
```html
<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="https://code.highcharts.com/modules/export-data.js"></script>
```

## Artifact Format

### Structure
```json
{
  "type": "artifact",
  "artifact_type": "chart",
  "title": "Chart Title",
  "description": "Brief description",
  "data": {
    // Highcharts configuration
  }
}
```

### Example Response
```
Here's your sales data:

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
      "data": [1000, 1500, 1200],
      "color": "#003B70"
    }]
  }
}
<<<ARTIFACT_END>>>

The data shows positive growth.
```

## Testing

### Test Artifact Rendering
1. Start the server: `source venv/bin/activate && python main.py`
2. Open http://localhost:8000
3. Type messages with keywords:
   - "Show me a chart"
   - "Visualize sales data"
   - "Create a graph"
   - "Show sales performance"

### Expected Behavior
- Message with keyword triggers artifact response
- Chart renders inline with text
- Text before/after artifact displays in separate bubbles
- Chart uses Citi bank colors (#003B70)
- Chart is interactive (hover, zoom, export)

## Customization

### Adding New Chart Types
Update `mockLLMResponse()` to return different chart configurations:

**Bar Chart:**
```json
{
  "chart": { "type": "bar" },
  "xAxis": { "categories": ["A", "B", "C"] },
  "series": [{ "data": [10, 20, 30] }]
}
```

**Pie Chart:**
```json
{
  "chart": { "type": "pie" },
  "series": [{
    "data": [
      { "name": "Category A", "y": 45 },
      { "name": "Category B", "y": 55 }
    ]
  }]
}
```

### Styling Charts
Modify chart configuration in `mockLLMResponse()`:
```json
{
  "colors": ["#003B70", "#D9261C"],
  "chart": {
    "backgroundColor": "#FFFFFF",
    "style": { "fontFamily": "system-ui" }
  }
}
```

## Integration with Real LLM

When connecting to a real LLM API:

1. **Send System Prompt:**
```python
from prompt import SYSTEM_PROMPT

response = llm_client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
)
```

2. **Return Response:**
The LLM will format responses with artifact markers when appropriate.

3. **Frontend Handles Detection:**
The `createArtifactMessage()` function automatically detects and renders artifacts.

## Error Handling

The implementation includes basic error handling:
- Invalid JSON in artifact is caught (will render as text)
- Missing Highcharts library falls back gracefully
- Chart rendering errors don't break the chat

## Future Enhancements

1. **Multiple Artifact Types:**
   - Tables
   - Code blocks
   - Images
   - Interactive forms

2. **Chart Interactions:**
   - Click to expand
   - Download as PNG/SVG
   - Edit chart data

3. **Database Integration:**
   - Query real data
   - Dynamic chart generation
   - Real-time updates

4. **Advanced Features:**
   - Multiple charts in one message
   - Chart comparisons
   - Animated transitions

