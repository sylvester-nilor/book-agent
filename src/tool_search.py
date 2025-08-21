import os
from langchain_core.tools import tool
import httpx
from auth import get_auth_session


def create_search_tool(search_service_url: str, auth_token: str = None):
    @tool
    def search_knowledge(query: str) -> str:
        """Search the knowledge base for relevant insights and information."""
        try:
            headers = {"Content-Type": "application/json"}

            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
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
            else:
                auth_session = get_auth_session()
                response = auth_session.post(
                    f"{search_service_url}/search",
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


if __name__ == "__main__":
    from auth import get_auth_token

    print("🔍 Testing Search Tool")

    _search_service_url = os.getenv("SEARCH_SERVICE_URL", "https://search-v1-959508709789.us-central1.run.app")
    _auth_token = get_auth_token()

    search_tool = create_search_tool(_search_service_url, _auth_token)

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
