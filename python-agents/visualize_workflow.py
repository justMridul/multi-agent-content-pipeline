"""
Script to visualize the LangGraph workflow structure.
This helps understand the graph structure and flow.
"""
from graph import create_workflow_async


def visualize_workflow():
    """Print the workflow structure and visualize it."""
    
    workflow = create_workflow_async()
    
    print("=" * 60)
    print("LangGraph Workflow Visualization")
    print("=" * 60)
    
    # Get the graph structure
    print("\nWorkflow Structure:")
    print("-" * 60)
    
    # Print the graph (LangGraph provides this)
    try:
        # Get the compiled graph
        graph = workflow.get_graph()
        print("\nNodes in the workflow:")
        for node in graph.nodes:
            print(f"  • {node}")
        
        print("\nEdges in the workflow:")
        for edge in graph.edges:
            print(f"  • {edge}")
            
    except AttributeError:
        # Fallback: manual description
        print("""
Workflow Flow:
  1. research (ResearchAgent)
     ↓
  2. write (WriterAgent)
     ↓
  3. fact_check (FactCheckerAgent)
     ↓
     ├─→ [if pass] → polish (PolisherAgent) → END
     └─→ [if fail] → write (loop back, max 3 iterations)
    
Conditional Logic:
  - fact_check_status == "pass" → proceed to polish
  - fact_check_status == "fail" → loop back to write
  - Max 3 iterations to prevent infinite loops
        """)
    
    print("\n" + "=" * 60)
    print("State Schema:")
    print("-" * 60)
    print("""
  • prd: Product Requirements Document (input)
  • topic: Blog post topic
  • target_length: Target word count
  • style: Writing style
  • research_data: Research findings from researcher
  • draft_content: Initial draft from writer
  • fact_checked_content: Content after fact-checking
  • fact_check_status: "pass" or "fail"
  • fact_check_iterations: Number of rewrite attempts
  • final_content: Final polished content
  • metadata: Additional metadata
    """)
    
    print("=" * 60)
    print("\nUsage:")
    print("-" * 60)
    print("""
1. Via FastAPI (recommended):
   POST http://localhost:8000/generate
   {
     "prd": "Your PRD here...",
     "topic": "Blog post topic",
     "target_length": 1000,
     "style": "professional"
   }

2. Programmatically:
   from graph import create_workflow_async
   workflow = create_workflow_async()
   result = await workflow.ainvoke({
     "prd": "...",
     "topic": "...",
     "target_length": 1000,
     "style": "professional",
     "fact_check_iterations": 0
   })

3. With streaming:
   async for event in workflow.astream(initial_state):
       print(event)  # See progress in real-time
    """)


if __name__ == "__main__":
    visualize_workflow()

