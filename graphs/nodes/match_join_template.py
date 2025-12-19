"""
M8: Match Join Template Node - Match questions to pre-defined JOIN templates.

This node analyzes the question complexity and suggests appropriate JOIN templates
to improve SQL generation quality for multi-table queries.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from graphs.state import NL2SQLState
from tools.join_template_matcher import join_template_library
from datetime import datetime


def match_join_template_node(state: NL2SQLState) -> NL2SQLState:
    """
    Match question to JOIN templates and analyze complexity.
    
    This node:
    1. Analyzes JOIN complexity of the question
    2. Finds matching templates from the library
    3. Provides few-shot examples for complex queries
    4. Updates state with template suggestions
    
    Args:
        state: Current NL2SQL state
        
    Returns:
        Updated state with JOIN template information
    """
    print(f"\n=== Match Join Template Node ===")
    
    question = state.get("question", "")
    
    # Analyze JOIN complexity
    analysis = join_template_library.analyze_join_complexity(question)
    
    print(f"Question: {question}")
    print(f"JOIN Complexity: {analysis['complexity']}")
    print(f"Estimated Tables: {analysis['table_count']}")
    print(f"Join Type: {analysis['join_type']}")
    print(f"Has Template Match: {analysis['has_template']}")
    
    if analysis['suggested_templates']:
        print(f"Suggested Templates ({len(analysis['suggested_templates'])}):")
        for i, template in enumerate(analysis['suggested_templates'], 1):
            print(f"  {i}. {template['name']} (score: {template['score']:.2f})")
            
        # Show best match example
        if analysis.get('best_match'):
            best = analysis['best_match']
            print(f"\n✓ Best Match: {best['name']}")
            print(f"  Tables: {', '.join(best['tables'])}")
            print(f"  Complexity: {best['complexity']}")
            print(f"  Example Question: {best['example_question']}")
    else:
        print(f"⚠️ No template match - will use generic SQL generation")
    
    return {
        **state,
        "join_complexity": analysis['complexity'],
        "suggested_templates": analysis['suggested_templates'],
        "template_matched_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    """Test match join template node."""
    
    print("="*70)
    print("Testing Match Join Template Node")
    print("="*70)
    
    test_cases = [
        "查询每个客户的订单总额",
        "查询所有专辑及其艺术家",
        "查询客户购买的所有歌曲",
        "查询每个客户最喜欢的音乐风格",
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
        
        result = match_join_template_node(state)
        
        print(f"\nResult:")
        print(f"  Complexity: {result['join_complexity']}")
        print(f"  Templates Found: {len(result['suggested_templates']) if result['suggested_templates'] else 0}")
    
    print("\n" + "="*70)
