import os
from typing import List, Dict, Any, Optional
import httpx
from google.auth.transport.requests import AuthorizedSession

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.auth import get_auth_token, get_auth_session


class SearchNode:
    def __init__(self, search_service_url: str, auth_token: Optional[str] = None):
        self.search_service_url = search_service_url
        self.auth_token = auth_token
        self._auth_session = None

    def _get_auth_session(self) -> AuthorizedSession:
        """Get an authenticated session for calling the search service."""
        if self._auth_session is None:
            self._auth_session = get_auth_session()
        return self._auth_session

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant book content based on the query."""
        try:
            headers = {"Content-Type": "application/json"}
            
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                return await self._search_with_token(query, limit, headers)
            else:
                # In production, use the service account credentials
                auth_session = self._get_auth_session()
                return await self._search_with_auth_session(query, limit, auth_session)
                
        except Exception as e:
            print(f"Error calling search service: {str(e)}")
            return []

    async def _search_with_token(self, query: str, limit: int, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Search using auth token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.search_service_url}/search",
                json={"query": query, "limit": limit},
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", [])

    async def _search_with_auth_session(self, query: str, limit: int, auth_session: AuthorizedSession) -> List[Dict[str, Any]]:
        """Search using the authenticated session (for production)."""
        try:
            response = auth_session.post(
                f"{self.search_service_url}/search",
                json={"query": query, "limit": limit},
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", [])
        except Exception as e:
            print(f"Error calling search service with auth session: {str(e)}")
            return []


if __name__ == "__main__":
    import asyncio
    
    async def test_search():
        search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")
        auth_token = get_auth_token()
        
        search_node = SearchNode(search_service_url, auth_token)
        
        # Test search functionality
        query = "What is digital sovereignty?"
        print(f"🔍 Testing search with query: '{query}'")
        
        results = await search_node.search(query, limit=3)
        
        if results:
            print(f"✅ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                book_id = result.get("book_id", "Unknown")
                page = result.get("page_number", "Unknown")
                content = result.get("content", "")[:100] + "..."
                print(f"  {i}. {book_id} (Page {page}): {content}")
        else:
            print("❌ No results found")
    
    asyncio.run(test_search())
