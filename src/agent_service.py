import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, TypedDict, Annotated

import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.auth.transport.requests import Request
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    search_results: Annotated[Optional[List[Dict[str, Any]]], "Results from search tool"]


class AgentService:
    def __init__(self, project_id: str, search_service_url: str, auth_token: Optional[str] = None):
        self.project_id = project_id
        self.search_service_url = search_service_url
        self.auth_token = auth_token
        self.memory_saver = MemorySaver()
        self.agent = self._build_agent()
        self._auth_session = None

    def _get_auth_session(self) -> AuthorizedSession:
        """Get an authenticated session for calling the search service."""
        if self._auth_session is None:
            credentials, _ = google.auth.default()
            if not credentials.valid:
                credentials.refresh(Request())
            self._auth_session = AuthorizedSession(credentials)
        return self._auth_session

    def _get_auth_token(self) -> str:
        """Get an authentication token for calling the search service."""
        credentials, _ = google.auth.default()
        if not credentials.valid:
            credentials.refresh(Request())
        return credentials.token

    def _build_agent(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("search", self._search_node)
        workflow.add_node("respond", self._respond_node)

        workflow.set_entry_point("search")
        workflow.add_edge("search", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile(checkpointer=self.memory_saver)

    async def search_tool(self, query: str) -> List[Dict[str, Any]]:
        """Search for relevant book content based on the query."""
        try:
            import httpx
            
            headers = {"Content-Type": "application/json"}
            
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            else:
                # In production, use the service account credentials
                auth_session = self._get_auth_session()
                return await self._search_with_auth_session(query, auth_session)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.search_service_url}/search",
                    json={"query": query, "limit": 5},
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result", [])
        except Exception as e:
            print(f"Error calling search service: {str(e)}")
            return []

    async def _search_with_auth_session(self, query: str, auth_session: AuthorizedSession) -> List[Dict[str, Any]]:
        """Search using the authenticated session (for production)."""
        try:
            response = auth_session.post(
                f"{self.search_service_url}/search",
                json={"query": query, "limit": 5},
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", [])
        except Exception as e:
            print(f"Error calling search service with auth session: {str(e)}")
            return []

    async def _search_node(self, state: AgentState) -> AgentState:
        """Node that performs search if needed."""
        messages = state["messages"]
        last_message = messages[-1]

        if isinstance(last_message, HumanMessage):
            search_results = await self.search_tool(last_message.content)
            return {"messages": messages, "search_results": search_results}

        return {"messages": messages, "search_results": []}

    async def _respond_node(self, state: AgentState) -> AgentState:
        """Node that generates the response."""
        messages = state["messages"]
        search_results = state.get("search_results", []) or []

        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            response_content = self._synthesize_response(
                user_message=last_message.content,
                search_results=search_results
            )

            ai_message = AIMessage(content=response_content)
            messages.append(ai_message)

        return {"messages": messages, "search_results": search_results}

    def _synthesize_response(self, user_message: str, search_results: List[Dict[str, Any]]) -> str:
        """Synthesize a conversational response from search results."""
        if not search_results:
            return "I couldn't find any relevant information in the books. Could you please rephrase your question or ask about a different topic?"

        response_parts = []
        response_parts.append("Based on the books, here's what I found:")

        for i, result in enumerate(search_results[:3], 1):
            book_id = result.get("book_id", "Unknown book")
            content = result.get("content", "")
            page_number = result.get("page_number", "")

            response_parts.append(f"\n{i}. From {book_id}")
            if page_number:
                response_parts.append(f"   (Page {page_number})")
            response_parts.append(f"   {content[:200]}{'...' if len(content) > 200 else ''}")

        response_parts.append(f"\n\nIs there anything specific about this information you'd like me to elaborate on?")

        return " ".join(response_parts)

    async def chat(self, message: str, thread_id: str) -> str:
        """Main chat method that handles the conversation."""
        try:
            config = {"configurable": {"thread_id": thread_id}}

            result = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=message)]},
                config=config
            )

            messages = result["messages"]
            if messages and isinstance(messages[-1], AIMessage):
                return messages[-1].content

            return "I'm sorry, I couldn't generate a response at this time."

        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"

    def _log_chat(self, thread_id: str, message: str, response: str,
                  execution_time: float, error_message: Optional[str] = None) -> None:
        """Log chat interactions for monitoring."""
        try:
            chat_log = {
                "thread_id": thread_id,
                "user_message": message,
                "agent_response": response,
                "execution_time": execution_time,
                "error_message": error_message,
                "inserted_at": datetime.now(timezone.utc).isoformat()
            }

            print(f"Chat log: {json.dumps(chat_log, indent=2)}")

        except Exception as e:
            print(f"Error logging chat: {str(e)}")


if __name__ == "__main__":
    import asyncio
    import subprocess


    async def test_chat():
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
            auth_token=auth_token
        )

        response = await service.chat(
            message="What is digital sovereignty?",
            thread_id="test-thread-123"
        )
        print(f"Response: {response}")


    asyncio.run(test_chat())
