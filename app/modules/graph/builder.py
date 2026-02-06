from .node import Node
from langchain_graph import START , END ,StateGraph
from .state import GraphState

Node_instance = Node()

def graph_builder():
     graph = StateGraph(GraphState)
     graph.add_node("router",Node_instance.router_node)
     graph.add_node("personal_setup",Node_instance.peronal_setup_node)
     graph.add_node("conversation",Node_instance.conversation_node)
     graph.add_node("conversation_with_image",Node_instance.conversation_node_with_image)
     graph.add_edge(START,"router")
     graph.add_edge(START,"personal_setup")
     graph.add_edge("personal_setup","conversation",condition=lambda state: state["workflow"] == "conversation")
     graph.add_edge("personal_setup","conversation_with_image",condition=lambda state: state["workflow"] == "conversation_with_image")
     graph.add_edge("conversation",END)
     graph.add_edge("conversation_with_image",END)
     return graph