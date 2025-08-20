from typing import List, Dict, Any

# No external imports needed for this module


class RespondNode:
    def __init__(self):
        pass

    def generate_response(self, user_message: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate a conversational response from search results."""
        if not search_results:
            return "I couldn't find any relevant information in the books. Could you please rephrase your question or ask about a different topic?"

        # Start with a conversational response
        response_parts = []
        
        # Add main response with natural citations
        response_parts.append("Based on the books, here's what I found:")
        
        # Process each search result with natural citations
        for i, result in enumerate(search_results[:3], 1):
            book_id = result.get("book_id", "Unknown book")
            content = result.get("content", "")
            page_number = result.get("page_number", "")
            
            # Create natural citation
            if page_number:
                citation = f"According to {book_id} (page {page_number})"
            else:
                citation = f"According to {book_id}"
            
            # Add citation and content
            response_parts.append(f"\n{citation}: {content[:200]}{'...' if len(content) > 200 else ''}")

        # Add conversational follow-up
        response_parts.append("\n\nIs there anything specific about this information you'd like me to elaborate on?")

        return " ".join(response_parts)

    def generate_greeting_response(self, user_message: str) -> str:
        """Generate a greeting response."""
        return "Hello! I'm here to help you find information about digital sovereignty and related topics from the books. What would you like to know?"

    def generate_thanks_response(self, user_message: str) -> str:
        """Generate a thanks response."""
        return "You're welcome! I'm glad I could help. Is there anything else you'd like to know about digital sovereignty or related topics?"

    def generate_goodbye_response(self, user_message: str) -> str:
        """Generate a goodbye response."""
        return "Goodbye! Feel free to come back if you have more questions about digital sovereignty and related topics."

    def generate_fallback_response(self, user_message: str) -> str:
        """Generate a fallback response when no search results are available."""
        return "I understand you're asking about this topic, but I don't have enough information to provide a comprehensive answer without searching the books. Could you please rephrase your question or ask something more specific about digital sovereignty, network states, or related concepts?"


if __name__ == "__main__":
    def test_response_generation():
        respond_node = RespondNode()
        
        # Test with mock search results
        mock_results = [
            {
                "book_id": "The Network State",
                "page_number": "83",
                "content": "Digital sovereignty refers to the ability of a network state to have root access to administrative functions and governance over its digital infrastructure."
            },
            {
                "book_id": "The Network State", 
                "page_number": "172",
                "content": "Limited sovereignty arrangements can open up new avenues for technological innovation while maintaining some legal power."
            }
        ]
        
        # Test response generation
        user_message = "What is digital sovereignty?"
        print(f"💬 Testing response generation for: '{user_message}'")
        
        response = respond_node.generate_response(user_message, mock_results)
        print(f"✅ Generated response:\n{response}")
        
        # Test greeting
        print(f"\n💬 Testing greeting response")
        greeting = respond_node.generate_greeting_response("Hello")
        print(f"✅ Greeting: {greeting}")
        
        # Test thanks
        print(f"\n💬 Testing thanks response")
        thanks = respond_node.generate_thanks_response("Thank you")
        print(f"✅ Thanks: {thanks}")
        
        # Test no results
        print(f"\n💬 Testing no results response")
        no_results = respond_node.generate_response("What is quantum computing?", [])
        print(f"✅ No results: {no_results}")
    
    test_response_generation()
