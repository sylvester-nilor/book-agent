import os
from typing import Optional
from langchain_core.tools import tool
import httpx

from auth import get_auth_token, get_auth_session


class SearchTool:
    def __init__(self, search_service_url: str, auth_token: Optional[str] = None):
        self.search_service_url = search_service_url
        self.auth_token = auth_token
        self._auth_session = None

    def _get_auth_session(self):
        if self._auth_session is None:
            self._auth_session = get_auth_session()
        return self._auth_session

    def create_search_tool(self):
        @tool
        def search_knowledge(query: str) -> str:
            try:
                headers = {"Content-Type": "application/json"}
                
                if self.auth_token:
                    headers["Authorization"] = f"Bearer {self.auth_token}"
                    with httpx.Client() as client:
                        response = client.post(
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
