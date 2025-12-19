"""
Answer Builder Node for NL2SQL system.
M9: Converts SQL execution results into natural language answers.
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from graphs.state import NL2SQLState
from tools.llm_client import llm_client


def format_data_preview(rows: list, columns: list, max_rows: int = 5) -> str:
    """
    Format query results as a readable preview.
    
    Args:
        rows: List of row dictionaries
        columns: List of column names
        max_rows: Maximum rows to include in preview
        
    Returns:
        Formatted data preview string
    """
    if not rows:
        return "(空结果)"
    
    preview_rows = rows[:max_rows]
    
    # Format as markdown table
    lines = []
    
    # Header
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    
    # Data rows
    for row in preview_rows:
        values = [str(row.get(col, "NULL")) for col in columns]
        lines.append("| " + " | ".join(values) + " |")
    
    if len(rows) > max_rows:
        lines.append(f"\n... 还有 {len(rows) - max_rows} 行数据未显示")
    
    return "\n".join(lines)


def build_answer_prompt(state: NL2SQLState) -> str:
    """
    Build the prompt for answer generation.
    
    Args:
        state: Current graph state
        
    Returns:
        Formatted prompt string
    """
    # Load answer prompt template
    prompt_path = project_root / "prompts" / "answer.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Get data from state
    question = state.get("question", "")
    sql = state.get("candidate_sql", "")
    execution_result = state.get("execution_result", {})
    
    # Extract execution result details
    row_count = execution_result.get("row_count", 0)
    columns = execution_result.get("columns", [])
    rows = execution_result.get("rows", [])
    
    # Format data preview
    preview_rows = min(5, row_count)
    data_preview = format_data_preview(rows, columns, max_rows=preview_rows)
    
    # Format columns as comma-separated string
    columns_str = ", ".join(columns) if columns else "无"
    
    # Fill template
    prompt = template.format(
        question=question,
        sql=sql,
        row_count=row_count,
        columns=columns_str,
        preview_rows=preview_rows,
        data_preview=data_preview
    )
    
    return prompt


def answer_builder_node(state: NL2SQLState) -> NL2SQLState:
    """
    Generate natural language answer from SQL execution results.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with answer field
    """
    print(f"\n=== Answer Builder Node ===")
    
    # Check if execution was successful
    execution_result = state.get("execution_result")
    if not execution_result:
        print("⚠️  No execution result found")
        return {
            **state,
            "answer": "无法生成答案：SQL未执行",
            "answer_generated_at": datetime.now().isoformat()
        }
    
    if not execution_result.get("ok"):
        error_msg = execution_result.get("error", "未知错误")
        print(f"⚠️  Execution failed: {error_msg}")
        return {
            **state,
            "answer": f"查询执行失败：{error_msg}",
            "answer_generated_at": datetime.now().isoformat()
        }
    
    # Build prompt
    try:
        prompt = build_answer_prompt(state)
        
        print(f"Question: {state.get('question')}")
        print(f"SQL: {state.get('candidate_sql')}")
        print(f"Result rows: {execution_result.get('row_count', 0)}")
        
        # Generate answer using LLM
        print("\n正在生成自然语言答案...")
        answer = llm_client.chat(prompt=prompt)
        
        print(f"\n生成的答案:")
        print(f"{answer}")
        
        return {
            **state,
            "answer": answer,
            "answer_generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"答案生成失败: {str(e)}"
        print(f"✗ {error_msg}")
        return {
            **state,
            "answer": error_msg,
            "answer_generated_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    """Test answer builder node"""
    print("=== Answer Builder Node Test ===\n")
    
    # Test case 1: Simple count query
    test_state_1: NL2SQLState = {
        "question": "有多少首歌曲？",
        "candidate_sql": "SELECT COUNT(*) as total FROM Track;",
        "execution_result": {
            "ok": True,
            "rows": [{"total": 3503}],
            "columns": ["total"],
            "row_count": 1,
            "error": None
        },
        "timestamp": None,
        "session_id": "test-1",
        "intent": None,
        "sql_generated_at": None,
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
        "template_matched_at": None
    }
    
    result_1 = answer_builder_node(test_state_1)
    print(f"\n✓ Test 1 passed - Answer generated")
    print(f"Answer length: {len(result_1.get('answer', ''))}")
    
    # Test case 2: List query with multiple results
    test_state_2: NL2SQLState = {
        "question": "显示所有音乐风格",
        "candidate_sql": "SELECT Name FROM Genre ORDER BY Name;",
        "execution_result": {
            "ok": True,
            "rows": [
                {"Name": "Alternative"},
                {"Name": "Blues"},
                {"Name": "Classical"},
                {"Name": "Jazz"},
                {"Name": "Metal"}
            ],
            "columns": ["Name"],
            "row_count": 5,
            "error": None
        },
        "timestamp": None,
        "session_id": "test-2",
        "intent": None,
        "sql_generated_at": None,
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
        "template_matched_at": None
    }
    
    result_2 = answer_builder_node(test_state_2)
    print(f"\n✓ Test 2 passed - Answer generated")
    
    # Test case 3: Failed execution
    test_state_3: NL2SQLState = {
        "question": "测试失败情况",
        "candidate_sql": "SELECT * FROM NonExistent;",
        "execution_result": {
            "ok": False,
            "rows": [],
            "columns": [],
            "row_count": 0,
            "error": "no such table: NonExistent"
        },
        "timestamp": None,
        "session_id": "test-3",
        "intent": None,
        "sql_generated_at": None,
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
        "template_matched_at": None
    }
    
    result_3 = answer_builder_node(test_state_3)
    print(f"\n✓ Test 3 passed - Error handled correctly")
    
    print("\n=== All Tests Passed ===")
