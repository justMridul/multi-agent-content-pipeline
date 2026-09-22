from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Literal, Optional
from agents.researcher import ResearchAgent
from agents.writer import WriterAgent
from agents.fact_checker import FactCheckerAgent
from agents.polisher import PolisherAgent


class WorkflowState(TypedDict):
    prd: Annotated[str, "Product Requirements Document"]
    topic: str
    target_length: Annotated[int, "Target length for the content"]
    style: Annotated[str, "Writing style"]
    post_id: Annotated[Optional[int], "ID of the post in the posts table"]
    research_data: Annotated[dict, "Research findings"]
    draft_content: Annotated[str, "Initial draft"]
    fact_checked_content: Annotated[str, "Content after fact checking"]
    fact_check_status: Annotated[Literal["pass", "fail"], "Fact check result"]
    fact_check_iterations: Annotated[int, "Number of fact check iterations"]
    final_content: Annotated[str, "Final polished content"]
    metadata: Annotated[dict, "Additional metadata"]


def should_continue_to_polish(state: WorkflowState) -> Literal["polish", "write"]:
    """
    Conditional edge function: determines if fact-check passed or should loop back to writer.
    
    Args:
        state: Current workflow state
        
    Returns:
        "polish" if fact check passed, "write" if it failed
    """
    status = state.get("fact_check_status", "fail")
    iterations = state.get("fact_check_iterations", 0)
    max_iterations = 3  # Prevent infinite loops
    
    if status == "pass":
        return "polish"
    elif iterations >= max_iterations:
        # After max iterations, proceed anyway to avoid infinite loop
        print(f"Warning: Fact check failed after {iterations} iterations, proceeding to polish")
        return "polish"
    else:
        print(f"Fact check failed, rewriting (iteration {iterations + 1}/{max_iterations})")
        return "write"


def create_workflow():
    """
    Create and compile the LangGraph workflow for the multi-agent content pipeline.
    
    Flow: PRD → Researcher → Writer → Fact-Checker → (pass: Polisher, fail: Writer) → Final
    """
    # Initialize agents
    researcher = ResearchAgent()
    writer = WriterAgent()
    fact_checker = FactCheckerAgent()
    polisher = PolisherAgent()
    
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("research", researcher.run)
    workflow.add_node("write", writer.run)
    workflow.add_node("fact_check", fact_checker.run)
    workflow.add_node("polish", polisher.run)
    
    # Define the flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "fact_check")
    
    # Conditional edge: fact_check → polish (if pass) or write (if fail)
    workflow.add_conditional_edges(
        "fact_check",
        should_continue_to_polish,
        {
            "polish": "polish",
            "write": "write"
        }
    )
    
    workflow.add_edge("polish", END)
    
    # Compile the graph
    return workflow.compile()


# Note: Conditional edges in LangGraph are always synchronous, even in async workflows
# So we reuse the same function for both sync and async workflows


def create_workflow_async():
    """
    Create an async version of the workflow.
    
    Flow: PRD → Researcher → Writer → Fact-Checker → (pass: Polisher, fail: Writer) → Final
    """
    # Initialize agents
    researcher = ResearchAgent()
    writer = WriterAgent()
    fact_checker = FactCheckerAgent()
    polisher = PolisherAgent()
    
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("research", researcher.run_async)
    workflow.add_node("write", writer.run_async)
    workflow.add_node("fact_check", fact_checker.run_async)
    workflow.add_node("polish", polisher.run_async)
    
    # Define the flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "fact_check")
    
    # Conditional edge: fact_check → polish (if pass) or write (if fail)
    # Note: Conditional edges are synchronous even in async workflows
    workflow.add_conditional_edges(
        "fact_check",
        should_continue_to_polish,
        {
            "polish": "polish",
            "write": "write"
        }
    )
    
    workflow.add_edge("polish", END)
    
    # Compile the graph
    return workflow.compile()

