import os
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from models.agent_state import AgentState
from nodes.search_node import SearchNode
from nodes.respond_node import RespondNode
from utils.auth import get_auth_token


class AgentService:
    def __init__(self, project_id: str, search_service_url: str, auth_token: Optional[str] = None):
        self.project_id = project_id
        self.search_service_url = search_service_url
        self.auth_token = auth_token
        self.memory_saver = MemorySaver()
        
        # Initialize nodes
        self.search_node = SearchNode(search_service_url, auth_token)
        self.respond_node = RespondNode()
        
        # Build agent
        self.agent = self._build_agent()

    def _build_agent(self):
        """Build the LangGraph agent workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("search", self._search_node)
        workflow.add_node("respond", self._respond_node)

        # Set entry point and edges
        workflow.set_entry_point("search")
        workflow.add_edge("search", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile(checkpointer=self.memory_saver)

    async def _search_node(self, state: AgentState) -> AgentState:
        """Node that performs search."""
        messages = state["messages"]
        last_message = messages[-1]

        if isinstance(last_message, HumanMessage):
            # Check if this is a simple greeting/thanks/goodbye
            query_lower = last_message.content.lower()
            
            if any(word in query_lower for word in ["hello", "hi", "hey"]):
                # Skip search for greetings
                return {"messages": messages, "search_results": []}
            
            if any(word in query_lower for word in ["thank", "thanks"]):
                # Skip search for thanks
                return {"messages": messages, "search_results": []}
            
            if any(word in query_lower for word in ["goodbye", "bye", "see you"]):
                # Skip search for goodbyes
                return {"messages": messages, "search_results": []}
            
            # Perform search for other queries
            search_results = await self.search_node.search(last_message.content)
            return {"messages": messages, "search_results": search_results}

        return {"messages": messages, "search_results": []}

    async def _respond_node(self, state: AgentState) -> AgentState:
        """Node that generates the response."""
        messages = state["messages"]
        search_results = state.get("search_results", []) or []

        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            # Generate appropriate response based on message type
            query_lower = last_message.content.lower()
            
            if any(word in query_lower for word in ["hello", "hi", "hey"]):
                response_content = self.respond_node.generate_greeting_response(last_message.content)
            elif any(word in query_lower for word in ["thank", "thanks"]):
                response_content = self.respond_node.generate_thanks_response(last_message.content)
            elif any(word in query_lower for word in ["goodbye", "bye", "see you"]):
                response_content = self.respond_node.generate_goodbye_response(last_message.content)
            elif search_results:
                response_content = self.respond_node.generate_response(last_message.content, search_results)
            else:
                response_content = self.respond_node.generate_fallback_response(last_message.content)

            ai_message = AIMessage(content=response_content)
            messages.append(ai_message)

        return {"messages": messages, "search_results": search_results}

    async def chat(self, message: str, thread_id: str) -> str:
        """Main chat method that handles the conversation."""
        try:
            config = {"configurable": {"thread_id": thread_id}}

            # Get existing state or create new one
            try:
                # Try to get existing state from checkpoint
                existing_state = await self.agent.aget_state(config)
                if existing_state:
                    # Add new message to existing conversation
                    existing_messages = existing_state["messages"]
                    existing_messages.append(HumanMessage(content=message))
                    initial_state = {
                        **existing_state,
                        "messages": existing_messages
                    }
                else:
                    # Create new state
                    initial_state = {
                        "messages": [HumanMessage(content=message)],
                        "search_results": None
                    }
            except Exception:
                # If no existing state, create new one
                initial_state = {
                    "messages": [HumanMessage(content=message)],
                    "search_results": None
                }

            result = await self.agent.ainvoke(initial_state, config=config)

            messages = result["messages"]
            if messages and isinstance(messages[-1], AIMessage):
                return messages[-1].content

            return "I'm sorry, I couldn't generate a response at this time."

        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"


if __name__ == "__main__":
    import asyncio

    async def test_conversation():
        project_id = os.getenv("GCP_PROJECT", "robot-rnd-nilor-gcp")
        search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")
        auth_token = get_auth_token()

        service = AgentService(
            project_id=project_id,
            search_service_url=search_service_url,
            auth_token=auth_token
        )

        # Test conversation
        thread_id = "test-conversation-123"
        
        print("=== Testing full conversation ===")
        
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

    asyncio.run(test_conversation())
