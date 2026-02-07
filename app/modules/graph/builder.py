from .node import Node
from langgraph.graph import START, END, StateGraph
from .state import GraphState

Node_instance = Node()


def route_after_router(state: GraphState) -> str:
     """Route based on workflow decision"""
     workflow = state.get("workflow", "conversation")
     if workflow == "conversation_with_image":
          return "conversation_with_image"
     return "conversation"


def graph_builder():
     graph = StateGraph(GraphState)
     
     # Add all nodes
     graph.add_node("router", Node_instance.router_node)
     graph.add_node("personal_setup", Node_instance.personal_setup_node)
     graph.add_node("generate_title", Node_instance.generate_title)
     graph.add_node("conversation", Node_instance.conversation_node)
     graph.add_node("conversation_with_image", Node_instance.conversation_node_with_image)
     graph.add_node("summary", Node_instance.summary_node)
     
     # Define edges
     graph.add_edge(START, "personal_setup")
     graph.add_edge(START, "router")
     graph.add_edge(START, "generate_title")
     
     # Conditional routing after router based on workflow
     graph.add_conditional_edges(
          "router",
          route_after_router,
          {
               "conversation": "conversation",
               "conversation_with_image": "conversation_with_image"
          }
     )
     
     # Both conversation nodes go to summary
     graph.add_edge("conversation", "summary")
     graph.add_edge("conversation_with_image", "summary")
     graph.add_edge("summary", END)
     
     return graph