from langgraph.graph import StateGraph, END
from .state import ProjectState
from .agent_visionary import visionary_agent
from .agent_architect import architect_agent
from .agent_constructor import constructor_node

def create_graph():
    workflow = StateGraph(ProjectState)

    # Add nodes
    workflow.add_node("visionary", visionary_agent)
    workflow.add_node("architect", architect_agent)
    workflow.add_node("constructor", constructor_node)

    # Define edges
    workflow.set_entry_point("visionary")
    workflow.add_edge("visionary", "architect")
    workflow.add_edge("architect", "constructor")
    workflow.add_edge("constructor", END)

    return workflow.compile()

graph = create_graph()
