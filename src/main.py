import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent_service import AgentService

app = FastAPI(title="Knowledge Agent", version="1.0.0")

# Create ONE instance that persists across all requests
project_id = os.getenv("GCP_PROJECT", "robot-rnd-nilor-gcp")
search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")

agent_service = AgentService(
    project_id=project_id,
    search_service_url=search_service_url
)


class ChatRequest(BaseModel):
    message: str
    thread_id: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def health_check():
    return {"status": "healthy", "service": "knowledge-agent"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        # Use the SAME instance every time
        response = agent_service.chat(
            message=request.message,
            thread_id=request.thread_id
        )

        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    import httpx
    import subprocess
    import time

    # Test memory persistence
    print("🧪 Testing Memory Persistence")
    print("=" * 50)
    
    # Start server in background
    print("🚀 Starting server...")
    import threading
    import sys
    
    def run_server():
        uvicorn.run(app, host='0.0.0.0', port=8080)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Get auth token
        auth_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token"],
            text=True,
            stderr=subprocess.PIPE
        ).strip()
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        thread_id = "test-main-memory-123"
        
        # Test conversation
        print("📝 Message 1: Remembering favorite color...")
        response1 = httpx.post(
            "http://localhost:8080/chat",
            json={"message": "Remember this: my favorite color is purple", "thread_id": thread_id},
            headers=headers
        )
        response1_data = response1.json()
        print(f"Response 1: {response1_data['response']}")
        
        print("\n📝 Message 2: Asking about favorite color...")
        response2 = httpx.post(
            "http://localhost:8080/chat",
            json={"message": "What is my favorite color?", "thread_id": thread_id},
            headers=headers
        )
        response2_data = response2.json()
        print(f"Response 2: {response2_data['response']}")
        
        # Check if memory worked
        if "purple" in response2_data['response'].lower():
            print("\n✅ Memory test PASSED - Agent remembered the color!")
        else:
            print("\n❌ Memory test FAILED - Agent forgot the color!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Starting server...")
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
