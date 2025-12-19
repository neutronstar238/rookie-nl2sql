"""
M7: Clarify Intent Node - Multi-turn clarification and intent disambiguation.

This node detects ambiguous questions and decides whether to request clarification.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from graphs.state import NL2SQLState
from tools.ambiguity_detector import clarification_manager
from datetime import datetime


def clarify_intent_node(state: NL2SQLState) -> NL2SQLState:
    """
    Clarify user intent and detect ambiguities.
    
    This node:
    1. Analyzes the question for ambiguities
    2. Generates clarification questions if needed
    3. Normalizes the question if possible
    4. Updates state with clarification info
    
    Args:
        state: Current NL2SQL state
        
    Returns:
        Updated state with clarification information
    """
    print(f"\n=== Clarify Intent Node ===")
    
    question = state.get("question", "")
    session_id = state.get("session_id")
    
    # Check for ambiguities
    result = clarification_manager.check_and_clarify(question, session_id)
    
    print(f"Original Question: {question}")
    print(f"Ambiguity Score: {result['ambiguity_score']:.2f}")
    print(f"Needs Clarification: {'Yes' if result['needs_clarification'] else 'No'}")
    
    if result['needs_clarification']:
        print(f"⚠️ Ambiguous question detected!")
        print(f"Clarification Questions:")
        for i, q in enumerate(result['clarification_questions'], 1):
            print(f"  {i}. {q}")
    
    if result['normalized_question'] != question:
        print(f"✓ Normalized Question: {result['normalized_question']}")
    else:
        print(f"✓ Question is clear, no normalization needed")
    
    # Determine if we can proceed
    can_proceed = result['can_proceed']
    print(f"Can Proceed: {'Yes' if can_proceed else 'No'}")
    
    # Update question if normalized
    updated_question = result['normalized_question'] if can_proceed else question
    
    return {
        **state,
        "question": updated_question,  # Use normalized version
        "clarification_needed": result['needs_clarification'],
        "clarification_questions": result['clarification_questions'],
        "ambiguity_score": result['ambiguity_score'],
        "normalized_question": result['normalized_question'],
        "clarified_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    """Test clarify intent node."""
    
    print("="*70)
    print("Testing Clarify Intent Node")
    print("="*70)
    
    test_cases = [
        "查询所有客户",
        "查询最近的订单",
        "查询销售额很多的客户",
        "查询前10个产品",
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n### Test {i}: {question} ###")
        
        state: NL2SQLState = {
            "question": question,
            "session_id": f"test_{i}",
            "timestamp": None,
            "intent": None,
            "candidate_sql": None,
            "sql_generated_at": None,
            "execution_result": None,
            "executed_at": None,
            "schema": None,
            "schema_loaded_at": None,
            "validation_result": None,
            "validated_at": None,
            "sandbox_check": None,
            "sandbox_checked_at": None,
            "rag_evidence": None,
            "rag_retrieved_at": None,
            "clarification_needed": None,
            "clarification_questions": None,
            "ambiguity_score": None,
            "normalized_question": None,
            "clarified_at": None,
            "join_complexity": None,
            "suggested_templates": None,
            "template_matched_at": None,
        }
        
        result = clarify_intent_node(state)
        
        print(f"\nResult:")
        print(f"  Normalized: {result['normalized_question']}")
        print(f"  Needs Clarification: {result['clarification_needed']}")
        print(f"  Ambiguity Score: {result['ambiguity_score']:.2f}")
    
    print("\n" + "="*70)
