from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
     """State for the graph"""
     messages: Annotated[list, add_messages]
     workflow: str
     personal_setup: str
     summary: str
     title: str
     generated_image: str