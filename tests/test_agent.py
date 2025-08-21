import asyncio
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent_service import AgentService
from auth import get_auth_token


def test_agent():
    """Test the full agent conversation."""
    project_id = os.getenv("GCP_PROJECT", "robot-rnd-nilor-gcp")
    search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")

    service = AgentService(
        project_id=project_id,
        search_service_url=search_service_url
    )

    # Test conversation
    thread_id = "test-agent-123"
    
    print("=== Testing Agent Service ===")
    
    # Test greeting
    response1 = service.chat("Hello!", thread_id)
    print(f"Greeting: {response1}")
    print()
    
    # Test search query
    response2 = service.chat("What is digital sovereignty?", thread_id)
    print(f"Search query: {response2}")
    print()
    
    # Test follow-up
    response3 = service.chat("How does it relate to network states?", thread_id)
    print(f"Follow-up: {response3}")
    print()
    
    # Test thanks
    response4 = service.chat("Thank you!", thread_id)
    print(f"Thanks: {response4}")


if __name__ == "__main__":
    test_agent()
