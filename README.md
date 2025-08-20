# Book Agent - Modular RAG Agent

A conversational RAG (Retrieval-Augmented Generation) agent that searches through books and provides natural, cited responses.

## Architecture

The agent is built with a clean modular structure for easy development and testing:

```
src/
├── agent_service.py          # Main service + full conversation testing
├── nodes/
│   ├── search_node.py        # Search logic + search testing
│   └── respond_node.py       # Response generation + response testing
├── models/
│   └── agent_state.py        # AgentState TypedDict definition
└── utils/
    └── auth.py               # Authentication helpers + auth testing
tests/                        # Test files
├── test_agent.py
└── test_multi_turn.py
```

## Features

- **Natural Conversation**: Handles greetings, thanks, goodbyes without searching
- **Smart Search**: Searches books for relevant content when needed
- **Natural Citations**: Cites books naturally ("According to The Network State...")
- **Conversation Persistence**: Maintains conversation state across turns
- **Modular Design**: Each component can be tested independently

## Development Workflow

### Quick Testing

Test each component in isolation:

```bash
# Test search functionality
python src/nodes/search_node.py

# Test response generation
python src/nodes/respond_node.py

# Test authentication
python src/utils/auth.py

# Test full agent conversation
python src/agent_service.py

# Test from tests directory
python tests/test_agent.py
```

### Component Details

#### Search Node (`nodes/search_node.py`)
- Makes HTTP calls to search service
- Handles authentication (token or ADC)
- Returns structured search results

#### Respond Node (`nodes/respond_node.py`)
- Generates conversational responses
- Creates natural citations
- Handles different message types (greeting, thanks, search results)

#### Agent Service (`agent_service.py`)
- Orchestrates the LangGraph workflow
- Manages conversation state
- Routes messages to appropriate handlers

## Usage

The agent provides a simple chat interface:

```python
from src.agent_service import AgentService

service = AgentService(
    project_id="your-project",
    search_service_url="https://search-service-url",
    auth_token="your-auth-token"
)

response = await service.chat(
    message="What is digital sovereignty?",
    thread_id="conversation-123"
)
```

## Environment Variables

- `GCP_PROJECT`: Google Cloud project ID
- `SEARCH_SERVICE_URL`: URL of the search service
- `AUTH_TOKEN`: Authentication token (optional, uses ADC if not provided)

## Testing

Each component has built-in smoke tests that run when executed directly:

- **Search Node**: Tests search with sample query
- **Respond Node**: Tests response generation with mock data
- **Auth Utils**: Tests token retrieval
- **Agent Service**: Tests full conversation flow

This modular structure makes it easy to iterate on individual components without the complexity of the full system.
