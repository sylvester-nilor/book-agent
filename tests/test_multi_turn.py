import asyncio
import subprocess
import os
from agent_service import AgentService

async def test_multi_turn():
    project_id = os.getenv("GCP_PROJECT", "robot-rnd-nilor-gcp")
    search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")

    # Get auth token from gcloud CLI
    try:
        auth_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token"],
            text=True,
            stderr=subprocess.PIPE
        ).strip()
        print(f"Got auth token: {auth_token[:20]}...")
    except subprocess.CalledProcessError as e:
        print(f"Error getting auth token: {e}")
        auth_token = None

    service = AgentService(
        project_id=project_id,
        search_service_url=search_service_url,
        auth_token=auth_token,
        max_turns=3
    )

    # Test multi-turn conversation
    thread_id = "test-multi-turn-123"
    
    print("=== Turn 1: Initial Question ===")
    response1 = await service.chat(
        message="What is digital sovereignty?",
        thread_id=thread_id
    )
    print(f"Response: {response1}")
    print()

    print("=== Turn 2: Follow-up Question ===")
    response2 = await service.chat(
        message="How does it relate to network states?",
        thread_id=thread_id
    )
    print(f"Response: {response2}")
    print()

    print("=== Turn 3: Another Follow-up ===")
    response3 = await service.chat(
        message="Can you explain more about limited sovereignty?",
        thread_id=thread_id
    )
    print(f"Response: {response3}")
    print()

    print("=== Turn 4: Should hit max turns ===")
    response4 = await service.chat(
        message="What about the governance aspects?",
        thread_id=thread_id
    )
    print(f"Response: {response4}")

if __name__ == "__main__":
    asyncio.run(test_multi_turn())
