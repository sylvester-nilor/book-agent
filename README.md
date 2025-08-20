# Book Agent - Proactive Knowledge Agent

A conversational AI agent that proactively enriches natural conversations with relevant insights from a knowledge base. The agent engages in genuine dialogue while intelligently searching for and weaving in relevant knowledge when it could add value to the conversation.

## Architecture

The agent uses a simplified single-node architecture for natural conversation flow:

```
src/
├── agent_service.py          # Main service with LangGraph workflow
├── nodes/
│   └── llm_node.py          # Single LLM node with search tool integration
├── models/
│   └── agent_state.py       # AgentState TypedDict definition
└── utils/
    └── auth.py              # Authentication helpers
tests/                       # Test files
├── test_agent.py
└── test_multi_turn.py
```

## Features

- **Proactive Knowledge Search**: Intelligently searches for relevant insights when they could enhance the conversation
- **Natural Conversation Flow**: Engages in genuine dialogue without forcing search results
- **Contextual Intelligence**: Decides when to search based on conversational context, not user requests
- **Conversation Persistence**: Maintains conversation state across turns
- **Seamless Integration**: Weaves knowledge naturally into responses without academic citations

## Development Workflow

### Quick Testing

Test the proactive knowledge agent:

```bash
# Test the LLM node with proactive search
cd src && uv run python nodes/llm_node.py

# Test full agent conversation
cd src && uv run python agent_service.py

# Test from tests directory
cd src && uv run pytest
```

### Component Details

#### LLM Node (`nodes/llm_node.py`)
- Single LLM agent with integrated search tool
- Proactive knowledge search based on conversational context
- Natural conversation flow with intelligent search integration
- Comprehensive system prompt for proactive behavior

#### Agent Service (`agent_service.py`)
- Simplified LangGraph workflow with single LLM node
- Manages conversation state and persistence
- Handles natural conversation with proactive knowledge enrichment

## Usage

The agent provides a conversational interface that proactively enriches discussions:

```python
# From the src directory
from agent_service import AgentService

service = AgentService(
    project_id="your-project",
    search_service_url="https://search-service-url",
    auth_token="your-auth-token"
)

# The agent will proactively search for relevant insights when helpful
response = await service.chat(
    message="I've been working on an art project and got blocked",
    thread_id="conversation-123"
)
```

## Example Interactions

- **User**: "I've been working on an art project and got blocked"
- **Agent**: *searches "creative blocks art inspiration"* then responds conversationally with relevant insights about creativity/constraints

- **User**: "My startup is struggling with decision-making as we grow"
- **Agent**: *searches "organizational decision making scaling"* then weaves relevant concepts naturally into helpful conversation

The agent feels like talking to someone who's well-read and thoughtful, not like querying a database.

## Environment Variables

- `GCP_PROJECT`: Google Cloud project ID
- `SEARCH_SERVICE_URL`: URL of the search service
- `AUTH_TOKEN`: Authentication token (optional, uses ADC if not provided)

## Testing

The agent includes comprehensive testing for proactive knowledge behavior:

- **LLM Node**: Tests proactive search integration with various conversation scenarios
- **Agent Service**: Tests full conversation flow with proactive knowledge enrichment
- **Built-in Tests**: Run when executed directly to verify proactive behavior

The simplified architecture focuses on natural conversation flow with intelligent knowledge integration.
