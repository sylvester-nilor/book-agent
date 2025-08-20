import os
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from models.agent_state import AgentState
from nodes.llm_node import LLMNode
from utils.auth import get_auth_token


class AgentService:
    def __init__(self, project_id: str, search_service_url: str, auth_token: Optional[str] = None):
        self.project_id = project_id
        self.search_service_url = search_service_url
        self.auth_token = auth_token
        self.memory_saver = MemorySaver()
        
        self.llm_node = LLMNode(search_service_url, auth_token)
        
        self.agent = self._build_agent()

    def _build_agent(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("llm", self._llm_node)

        workflow.set_entry_point("llm")
        workflow.add_edge("llm", END)

        return workflow.compile(checkpointer=self.memory_saver)

    async def _llm_node(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        last_message = messages[-1]

        if isinstance(last_message, HumanMessage):
            response_content = await self.llm_node.process_message(
                user_message=last_message.content,
                conversation_history=self._get_conversation_history(messages[:-1])
            )

            ai_message = AIMessage(content=response_content)
            messages.append(ai_message)

        return {"messages": messages, "search_results": None}

    def _get_conversation_history(self, messages) -> list:
        history = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        return history

    async def chat(self, message: str, thread_id: str) -> str:
        try:
            config = {"configurable": {"thread_id": thread_id}}

            try:
                existing_state = await self.agent.aget_state(config)
                if existing_state:
                    existing_messages = existing_state["messages"]
                    existing_messages.append(HumanMessage(content=message))
                    initial_state = {
                        **existing_state,
                        "messages": existing_messages
                    }
                else:
                    initial_state = {
                        "messages": [HumanMessage(content=message)],
                        "search_results": None
                    }
            except Exception:
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

        thread_id = "test-proactive-agent-123"
        
        print("=== Testing Proactive Knowledge Agent ===")
        
        print("\n--- Test 1: Creative Block ---")
        response1 = await service.chat("I've been working on an art project and got blocked", thread_id)
        print(f"User: I've been working on an art project and got blocked")
        print(f"Agent: {response1}")
        
        print("\n--- Test 2: Startup Decision-Making ---")
        response2 = await service.chat("My startup is struggling with decision-making as we grow", thread_id)
        print(f"User: My startup is struggling with decision-making as we grow")
        print(f"Agent: {response2}")
        
        print("\n--- Test 3: General Conversation ---")
        response3 = await service.chat("I'm thinking about learning something new", thread_id)
        print(f"User: I'm thinking about learning something new")
        print(f"Agent: {response3}")
        
        print("\n--- Test 4: Personal Challenge ---")
        response4 = await service.chat("I'm feeling overwhelmed with all my commitments lately", thread_id)
        print(f"User: I'm feeling overwhelmed with all my commitments lately")
        print(f"Agent: {response4}")

    asyncio.run(test_conversation())
