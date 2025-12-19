"""
Base LangGraph for NL2SQL system.
M0: Minimal runnable implementation with input/output nodes.
M1: Added SQL generation using prompt engineering.
M2: Added SQL execution using function call.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langgraph.graph import StateGraph, END
from datetime import datetime
import uuid
import json

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from graphs.state import NL2SQLState
from graphs.nodes.generate_sql import generate_sql_node
from graphs.nodes.execute_sql import execute_sql_node
from graphs.nodes.schema_ingestion import schema_ingestion_node  # M3
from graphs.nodes.validate_sql import validate_sql_node  # M4
from graphs.nodes.sandbox_check import sandbox_check_node  # M5
from graphs.nodes.rag_retrieval import rag_retrieval_node  # M6
from graphs.nodes.clarify_intent import clarify_intent_node  # M7
from graphs.nodes.match_join_template import match_join_template_node  # M8
from graphs.nodes.answer_builder import answer_builder_node  # M9


def parse_intent_node(state: NL2SQLState) -> NL2SQLState:
    """
    Parse user intent from the question.
    M0: Simple intent extraction with metadata.
    """
    question = state.get("question", "")

    # Simple intent parsing - will be enhanced in future modules
    intent = {
        "type": "query",
        "question_length": len(question),
        "has_keywords": any(kw in question.lower() for kw in ["查询", "多少", "什么", "哪些", "统计", "show", "what", "how many"]),
        "parsed_at": datetime.now().isoformat()
    }

    print(f"\n=== Parse Intent Node ===")
    print(f"Question: {question}")
    print(f"Intent: {json.dumps(intent, indent=2, ensure_ascii=False)}")

    return {
        **state,
        "intent": intent,
        "timestamp": datetime.now().isoformat()
    }


def echo_node(state: NL2SQLState) -> NL2SQLState:
    """
    Echo node - prints current state for verification.
    M0: Simple output verification.
    M1: Also shows generated SQL.
    M2: Also shows execution results.
    M4: Also shows validation results.
    M5: Also shows sandbox check results.
    M6: Also shows RAG evidence.
    M7: Also shows clarification info.
    M8: Also shows JOIN template matches.
    M9: Also shows natural language answer.
    """
    print(f"\n=== Echo Node ===")
    print(f"Session ID: {state.get('session_id')}")
    print(f"Question: {state.get('question')}")
    print(f"Intent: {json.dumps(state.get('intent', {}), indent=2, ensure_ascii=False)}")

    # M7: Show clarification info
    if state.get('clarification_needed'):
        print(f"\nClarification:")
        print(f"  Needed: ✓")
        print(f"  Ambiguity Score: {state.get('ambiguity_score', 0):.2f}")
        if state.get('normalized_question'):
            print(f"  Normalized: {state.get('normalized_question')}")

    # M8: Show JOIN template matches
    if state.get('join_complexity'):
        print(f"\nJOIN Analysis:")
        print(f"  Complexity: {state.get('join_complexity')}")
        templates = state.get('suggested_templates', [])
        if templates:
            print(f"  Matched Templates: {len(templates)}")
            print(f"  Best Match: {templates[0].get('name', 'N/A')}")

    # M6: Show RAG evidence
    rag_evidence = state.get('rag_evidence')
    if rag_evidence:
        print(f"\nRAG Evidence:")
        print(f"  Has Evidence: {'✓' if rag_evidence.get('has_evidence') else '✗'}")
        print(f"  Recognized Terms: {len(rag_evidence.get('recognized_terms', []))}")
        print(f"  Similar Examples: {len(rag_evidence.get('similar_examples', []))}")

    # M1: Show generated SQL
    candidate_sql = state.get('candidate_sql')
    if candidate_sql:
        print(f"\nGenerated SQL:")
        print(f"  {candidate_sql}")

    # M4: Show validation results
    validation_result = state.get('validation_result')
    if validation_result:
        print(f"\nValidation Result:")
        print(f"  Valid: {'✓' if validation_result.get('valid') else '✗'}")
        if validation_result.get('errors'):
            print(f"  Errors: {validation_result['errors']}")
        if validation_result.get('warnings'):
            print(f"  Warnings: {validation_result['warnings']}")
        if validation_result.get('repair_applied'):
            print(f"  Repairs Applied: {validation_result['repair_changes']}")

    # M5: Show sandbox check results
    sandbox_check = state.get('sandbox_check')
    if sandbox_check:
        print(f"\nSandbox Check:")
        print(f"  Allowed: {'✓' if sandbox_check.get('allowed') else '✗'}")
        print(f"  Risk Level: {sandbox_check.get('risk_level')}")
        if sandbox_check.get('modifications'):
            print(f"  Modifications: {list(sandbox_check['modifications'].keys())}")

    # M2: Show execution results
    execution_result = state.get('execution_result')
    if execution_result:
        print(f"\nExecution Result:")
        if execution_result.get('ok'):
            print(f"  ✓ Success")
            print(f"  Rows: {execution_result.get('row_count', 0)}")
            print(f"  Columns: {', '.join(execution_result.get('columns', []))}")
            # Show first row
            if execution_result.get('rows'):
                print(f"  First row: {execution_result['rows'][0]}")
        else:
            print(f"  ✗ Failed: {execution_result.get('error')}")

    # M9: Show natural language answer
    answer = state.get('answer')
    if answer:
        print(f"\n=== Natural Language Answer ===")
        print(answer)
        print(f"{'='*50}")

    print(f"Timestamp: {state.get('timestamp')}")
    print(f"\n{'='*50}\n")

    return state


def build_graph() -> StateGraph:
    """
    Build the base NL2SQL graph.
    M0: Minimal graph with parse_intent -> echo
    M1: Added generate_sql node: parse_intent -> generate_sql -> echo
    M2: Added execute_sql node: parse_intent -> generate_sql -> execute_sql -> echo
    M3: Added schema_ingestion node: parse_intent -> schema_ingestion -> generate_sql -> execute_sql -> echo
    M4: Added validate_sql node: parse_intent -> schema_ingestion -> generate_sql -> validate_sql -> execute_sql -> echo
    M5: Added sandbox_check node: ... -> validate_sql -> sandbox_check -> execute_sql -> ...
    M6: Added rag_retrieval node: parse_intent -> rag_retrieval -> schema_ingestion -> ...
    M7: Added clarify_intent node: parse_intent -> clarify_intent -> rag_retrieval -> ...
    M8: Added match_join_template node: ... -> rag_retrieval -> match_join_template -> schema_ingestion -> ...
    """
    # Create graph
    workflow = StateGraph(NL2SQLState)

    # Add nodes
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("clarify_intent", clarify_intent_node)  # M7: New node
    workflow.add_node("rag_retrieval", rag_retrieval_node)  # M6
    workflow.add_node("match_join_template", match_join_template_node)  # M8: New node
    workflow.add_node("schema_ingestion", schema_ingestion_node)  # M3
    workflow.add_node("generate_sql", generate_sql_node)  # M1
    workflow.add_node("validate_sql", validate_sql_node)  # M4
    workflow.add_node("sandbox_check", sandbox_check_node)  # M5
    workflow.add_node("execute_sql", execute_sql_node)    # M2
    workflow.add_node("answer_builder", answer_builder_node)  # M9
    workflow.add_node("echo", echo_node)

    # Define edges
    workflow.set_entry_point("parse_intent")
    workflow.add_edge("parse_intent", "clarify_intent")          # M7: Clarify ambiguous questions
    workflow.add_edge("clarify_intent", "rag_retrieval")         # M7: Then retrieve RAG evidence
    workflow.add_edge("rag_retrieval", "match_join_template")    # M8: Match JOIN templates
    workflow.add_edge("match_join_template", "schema_ingestion") # M8: Then load schema
    workflow.add_edge("schema_ingestion", "generate_sql")        # M3: Then generate SQL
    workflow.add_edge("generate_sql", "validate_sql")            # M4: Validate SQL
    workflow.add_edge("validate_sql", "sandbox_check")           # M5: Check security
    workflow.add_edge("sandbox_check", "execute_sql")            # M5: Then execute
    workflow.add_edge("execute_sql", "answer_builder")           # M9: Generate natural language answer
    workflow.add_edge("answer_builder", "echo")
    workflow.add_edge("echo", END)

    # Compile graph
    graph = workflow.compile()

    return graph


def run_query(question: str, session_id: str = None) -> NL2SQLState:
    """
    Run a single query through the graph.

    Args:
        question: Natural language question
        session_id: Optional session identifier

    Returns:
        Final state after graph execution
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    # Build graph
    graph = build_graph()

    # Initialize state
    initial_state: NL2SQLState = {
        "question": question,
        "session_id": session_id,
        "timestamp": None,
        "intent": None,
        "candidate_sql": None,        # M1
        "sql_generated_at": None,     # M1
        "execution_result": None,     # M2
        "executed_at": None,          # M2
        "schema": None,               # M3
        "schema_loaded_at": None,     # M3
        "validation_result": None,    # M4
        "validated_at": None,         # M4
        "sandbox_check": None,        # M5
        "sandbox_checked_at": None,   # M5
        "rag_evidence": None,         # M6
        "rag_retrieved_at": None,     # M6
        "clarification_needed": None, # M7
        "clarification_questions": None,  # M7
        "ambiguity_score": None,      # M7
        "normalized_question": None,  # M7
        "clarified_at": None,         # M7
        "join_complexity": None,      # M8
        "suggested_templates": None,  # M8
        "template_matched_at": None,  # M8
        "answer": None,               # M9
        "answer_generated_at": None   # M9
    }

    # Run graph
    print(f"\n{'='*50}")
    print(f"Starting NL2SQL Graph (M9 - Answer Builder)")
    print(f"{'='*50}")

    result = graph.invoke(initial_state)

    return result


if __name__ == "__main__":
    """
    M2 Acceptance Test:
    Input a question, generate SQL, and execute against database.
    """
    # Test cases - will work with Chinook database
    test_questions = [
        "Show all albums",
        "How many tracks are there?",
        "What are the top 5 longest tracks?"
    ]

    print("\n" + "="*70)
    print("M2 - NL2SQL with Function Call Test")
    print("="*70)

    for i, question in enumerate(test_questions, 1):
        print(f"\n### Test Case {i} ###")
        result = run_query(question)
        print(f"\nFinal State Keys: {list(result.keys())}")
        print(f"SQL Generated: {'✓' if result.get('candidate_sql') else '✗'}")
        exec_result = result.get('execution_result', {})
        print(f"SQL Executed: {'✓' if exec_result.get('ok') else '✗'}")

    print("\n" + "="*70)
    print("M2 Test Complete!")
    print("="*70)
