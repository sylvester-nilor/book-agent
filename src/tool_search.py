import os
from langchain_core.tools import tool
import httpx
import google.auth.transport.requests
import google.oauth2.id_token


def create_search_tool(search_service_url: str):
    @tool
    def search_knowledge(query: str) -> str:
        """Search the knowledge base for relevant insights and information."""
        try:
            id_token = os.environ.get("AUTH_TOKEN", None)
            
            if id_token is None:
                auth_req = google.auth.transport.requests.Request()
                id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience=search_service_url)
            
            headers = {"Authorization": f"Bearer {id_token}"}
            with httpx.Client() as client:
                response = client.post(
                    f"{search_service_url}/search",
                    json={"query": query, "limit": 3},
                    headers=headers,
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


if __name__ == "__main__":
    print("🔍 Testing Search Tool")

    _search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")

    search_tool = create_search_tool(_search_service_url)

    print(f"\n--- Test 1: Digital Sovereignty ---")
    result1 = search_tool.invoke({"query": "digital sovereignty"})
    print(f"Query: digital sovereignty")
    print(f"Result: {result1}")

    print(f"\n--- Test 2: Creative Blocks ---")
    result2 = search_tool.invoke({"query": "creative blocks motivation inspiration"})
    print(f"Query: creative blocks motivation inspiration")
    print(f"Result: {result2}")

    print(f"\n--- Test 3: Decision Making ---")
    result3 = search_tool.invoke({"query": "decision making organizational leadership"})
    print(f"Query: decision making organizational leadership")
    print(f"Result: {result3}")
