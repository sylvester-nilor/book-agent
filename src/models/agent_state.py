from typing import List, Dict, Any, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    search_results: Annotated[Optional[List[Dict[str, Any]]], "Results from search tool"]
