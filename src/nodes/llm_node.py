import os
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import google.auth

from utils.auth import get_auth_token, get_auth_session


class LLMNode:
    def __init__(self, search_service_url: str, auth_token: Optional[str] = None):
        self.search_service_url = search_service_url
        self.auth_token = auth_token
        self._auth_session = None
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=None,
            temperature=0.7,
            max_tokens=1000
        )
        
        self.search_tool = self._create_search_tool()
        
        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        return """You are a thoughtful, well-read conversational assistant with access to a rich knowledge base of books and insights. Your goal is to engage in natural, helpful conversations while proactively enriching discussions with relevant knowledge when it could add value.

## Your Approach:
- **Engage naturally**: Have genuine conversations on any topic the user brings up
- **Proactive knowledge**: When you sense that insights from your knowledge base could help, search for relevant concepts, themes, or ideas
- **Weave knowledge naturally**: Integrate search results conversationally into your responses, not as lectures or citations
- **Stay helpful**: Focus on being genuinely useful to the user's situation or interests
- **Conversational flow**: Keep the conversation flowing naturally - the user doesn't know what's in your knowledge base

## When to Search:
- When the user shares a problem, challenge, or situation that might benefit from broader insights
- When discussing topics that could be enriched with relevant concepts or frameworks
- When the user seems stuck, curious, or could benefit from a fresh perspective
- When you sense an opportunity to share relevant knowledge that could help
- When the conversation could benefit from deeper context or new perspectives

## How to Use Search Results:
- Don't cite sources or mention "the books" - just weave insights naturally
- Connect concepts to the user's specific situation or interests
- Share ideas that might offer new perspectives or approaches
- Keep responses conversational and engaging, not academic
- Use search results to enhance your understanding, not replace your conversational skills

## Examples:
- User: "I'm feeling stuck on this project" → Search for concepts about creative blocks, problem-solving, or motivation
- User: "My team is having communication issues" → Search for insights about collaboration, organizational dynamics, or leadership
- User: "I'm thinking about starting something new" → Search for ideas about innovation, risk-taking, or new beginnings
- User: "I'm overwhelmed with commitments" → Search for insights about prioritization, time management, or work-life balance

## Important Guidelines:
- You decide when to search based on conversational context
- Don't search for every message - only when it would genuinely add value
- If search results don't seem relevant, respond conversationally without forcing them in
- Always maintain natural conversation flow
- Be genuinely helpful and thoughtful, not just informative

Remember: You're having a conversation with someone who values thoughtful insights, not querying a database. Be genuinely helpful and conversational."""

    def _create_search_tool(self):
        
        @tool
        async def search_knowledge(query: str) -> str:
            try:
                import httpx
                
                headers = {"Content-Type": "application/json"}
                
                if self.auth_token:
                    headers["Authorization"] = f"Bearer {self.auth_token}"
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.search_service_url}/search",
                            json={"query": query, "limit": 3},
                            headers=headers,
                            timeout=30.0
                        )
                        response.raise_for_status()
                        result = response.json()
                        search_results = result.get("result", [])
                else:
                    auth_session = self._get_auth_session()
                    response = auth_session.post(
                        f"{self.search_service_url}/search",
                        json={"query": query, "limit": 3},
                        timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    search_results = result.get("result", [])
                
                if not search_results:
                    return "No relevant insights found in the knowledge base."
                
                formatted_results = []
                for result in search_results:
                    book_id = result.get("book_id", "Unknown")
                    content = result.get("content", "")
                    page = result.get("page_number", "")
                    
                    if page:
                        formatted_results.append(f"From {book_id} (page {page}): {content}")
                    else:
                        formatted_results.append(f"From {book_id}: {content}")
                
                return "\n\n".join(formatted_results)
                
            except Exception as e:
                return f"Error searching knowledge base: {str(e)}"
        
        return search_knowledge

    def _get_auth_session(self):
        if self._auth_session is None:
            self._auth_session = get_auth_session()
        return self._auth_session

    async def process_message(self, user_message: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        try:
            messages = [SystemMessage(content=self.system_prompt)]
            
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            messages.append(HumanMessage(content=user_message))
            
            llm_with_tools = self.llm.bind_tools([self.search_tool])
            
            response = await llm_with_tools.ainvoke(messages)
            
            return response.content
            
        except Exception as e:
            print(f"Error in LLM processing: {str(e)}")
            return "I'm having trouble processing that right now. Could you rephrase your message?"


if __name__ == "__main__":
    import asyncio
    
    async def test_llm_node():
        search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")
        auth_token = get_auth_token()
        
        llm_node = LLMNode(search_service_url, auth_token)
        
        print("🤖 Testing LLM Node with proactive knowledge search")
        print()
        
        print("=== Test 1: Creative Block ===")
        response1 = await llm_node.process_message("I've been working on an art project and got blocked")
        print(f"User: I've been working on an art project and got blocked")
        print(f"Agent: {response1}")
        print()
        
        print("=== Test 2: Startup Decision-Making ===")
        response2 = await llm_node.process_message("My startup is struggling with decision-making as we grow")
        print(f"User: My startup is struggling with decision-making as we grow")
        print(f"Agent: {response2}")
        print()
        
        print("=== Test 3: General Conversation ===")
        response3 = await llm_node.process_message("I'm thinking about learning something new")
        print(f"User: I'm thinking about learning something new")
        print(f"Agent: {response3}")
        print()
        
        print("=== Test 4: Personal Challenge ===")
        response4 = await llm_node.process_message("I'm feeling overwhelmed with all my commitments lately")
        print(f"User: I'm feeling overwhelmed with all my commitments lately")
        print(f"Agent: {response4}")
    
    asyncio.run(test_llm_node())
