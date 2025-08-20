import asyncio
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent_service import AgentService
from utils.auth import get_auth_token


async def test_agent():
    """Test the full agent conversation."""
    project_id = os.getenv("GCP_PROJECT", "robot-rnd-nilor-gcp")
    search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")
    auth_token = get_auth_token()

    service = AgentService(
        project_id=project_id,
        search_service_url=search_service_url,
        auth_token=auth_token
    )

    # Test conversation
    thread_id = "test-agent-123"
    
    print("=== Testing Agent Service ===")
    
    # Test greeting
    response1 = await service.chat("Hello!", thread_id)
    print(f"Greeting: {response1}")
    print()
    
    # Test search query
    response2 = await service.chat("What is digital sovereignty?", thread_id)
    print(f"Search query: {response2}")
    print()
    
    # Test follow-up
    response3 = await service.chat("How does it relate to network states?", thread_id)
    print(f"Follow-up: {response3}")
    print()
    
    # Test thanks
    response4 = await service.chat("Thank you!", thread_id)
    print(f"Thanks: {response4}")


if __name__ == "__main__":
    asyncio.run(test_agent())
