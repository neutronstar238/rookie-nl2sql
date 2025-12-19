"""
RAG Retrieval Node for NL2SQL system.
M6: Retrieves domain terminology hints and similar QA-SQL examples.
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from graphs.state import NL2SQLState
from tools.rag_retriever import rag_retriever


def rag_retrieval_node(state: NL2SQLState) -> NL2SQLState:
    """
    Retrieve RAG evidence (terminology hints + similar QA-SQL examples).
    
    This node should be called BEFORE SQL generation to provide:
    1. Domain terminology mappings
    2. Similar historical QA-SQL pairs
    
    Args:
        state: Current NL2SQL state
        
    Returns:
        Updated state with rag_evidence
    """
    question = state.get("question", "")
    
    print(f"\n=== RAG Retrieval Node ===")
    print(f"Question: {question}")
    
    # Retrieve RAG evidence
    evidence = rag_retriever.retrieve(question, top_k=3)
    
    print(f"\nRAG Evidence:")
    print(f"  Has Evidence: {'✓' if evidence['has_evidence'] else '✗'}")
    print(f"  Recognized Terms: {len(evidence['recognized_terms'])}")
    print(f"  Similar Examples: {len(evidence['similar_examples'])}")
    
    # Show terminology hints
    if evidence['terminology_hints']:
        print(f"\n{evidence['terminology_hints']}")
    
    # Show top similar example
    if evidence['similar_examples']:
        top_example = evidence['similar_examples'][0]
        print(f"\n最相似的历史查询:")
        print(f"  问题: {top_example['question']}")
        print(f"  相似度: {top_example['similarity']:.2f}")
        print(f"  SQL: {top_example['sql'][:100]}...")
    
    return {
        **state,
        "rag_evidence": evidence,
        "rag_retrieved_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    """Test RAG retrieval node"""
    print("=== RAG Retrieval Node Test ===\n")
    
    test_questions = [
        "查询所有客户的姓名和城市",
        "统计每个国家的客户数量",
        "查询销售额最高的前10个客户"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}")
        print(f"{'='*60}")
        
        test_state: NL2SQLState = {
            "question": question,
            "session_id": f"test-{i}",
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
            "rag_retrieved_at": None
        }
        
        result = rag_retrieval_node(test_state)
        
        evidence = result.get('rag_evidence', {})
        print(f"\n✓ RAG retrieval completed")
        print(f"  Has Evidence: {evidence.get('has_evidence')}")
        print(f"  Terms: {len(evidence.get('recognized_terms', []))}")
        print(f"  Examples: {len(evidence.get('similar_examples', []))}")
    
    print(f"\n{'='*60}")
    print("Test Complete!")
    print(f"{'='*60}")
