"""
SQL Generation Node for NL2SQL system.
M1: Uses prompt engineering to generate SQL from natural language.
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


def load_prompt_template(template_name: str) -> str:
    """
    Load prompt template from prompts/ directory.

    Args:
        template_name: Name of the template file (without extension)

    Returns:
        Template content as string
    """
    template_path = Path(__file__).parent.parent.parent / "prompts" / f"{template_name}.txt"

    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_sql_from_response(response: str) -> str:
    """
    Extract SQL from LLM response.
    Handles various response formats (with/without markdown code blocks).

    Args:
        response: LLM response text

    Returns:
        Extracted SQL statement
    """
    # Remove markdown code blocks
    if "```sql" in response:
        # Extract content between ```sql and ```
        start = response.find("```sql") + 6
        end = response.find("```", start)
        sql = response[start:end].strip()
    elif "```" in response:
        # Extract content between ``` and ```
        start = response.find("```") + 3
        end = response.find("```", start)
        sql = response[start:end].strip()
    else:
        # No code blocks, use the entire response
        sql = response.strip()

    # Clean up
    sql = sql.strip()

    # Ensure SQL ends with semicolon
    if not sql.endswith(";"):
        sql += ";"

    return sql


def generate_sql_node(state: NL2SQLState) -> NL2SQLState:
    """
    Generate SQL from natural language question using LLM.

    M1: Simple prompt engineering without schema or RAG.
          Schema will be added in M3, RAG in M6.

    Args:
        state: Current NL2SQL state

    Returns:
        Updated state with candidate_sql
    """
    question = state.get("question", "")

    print(f"\n=== Generate SQL Node ===")
    print(f"Question: {question}")

    # Load prompt template
    prompt_template = load_prompt_template("nl2sql")

    # M3: Use real schema from state if available
    schema_info = state.get("schema")
    if schema_info and schema_info.get("formatted"):
        schema_text = schema_info["formatted"]
        print(f"✓ Using real schema ({schema_info.get('table_count', 0)} tables)")
    else:
        # Fallback to placeholder if schema not available
        schema_text = """
    Chinook 音乐商店数据库表结构:
    - Album (AlbumId, Title, ArtistId)
    - Artist (ArtistId, Name)
    - Track (TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice)
    - Genre (GenreId, Name)
    - Customer (CustomerId, FirstName, LastName, Company, Address, City, State, Country, PostalCode, Phone, Fax, Email, SupportRepId)
    - Invoice (InvoiceId, CustomerId, InvoiceDate, BillingAddress, BillingCity, BillingState, BillingCountry, BillingPostalCode, Total)
    - InvoiceLine (InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity)
    - Employee (EmployeeId, LastName, FirstName, Title, ReportsTo, BirthDate, HireDate, Address, City, State, Country, PostalCode, Phone, Fax, Email)
    - Playlist (PlaylistId, Name)
    - PlaylistTrack (PlaylistId, TrackId)
    - MediaType (MediaTypeId, Name)
    
    注意: 表名和列名都使用 Pascal Case (首字母大写)
    """
        print(f"⚠️  Using fallback schema (schema not in state)")

    # Fill in the prompt template
    prompt = prompt_template.format(
        schema=schema_text.strip(),
        question=question
    )

    try:
        # Call LLM
        response = llm_client.chat(prompt=prompt)

        print(f"\nLLM Response:\n{response}")

        # Extract SQL from response
        candidate_sql = extract_sql_from_response(response)

        print(f"\nExtracted SQL:\n{candidate_sql}")

        return {
            **state,
            "candidate_sql": candidate_sql,
            "sql_generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"\n✗ Error generating SQL: {e}")

        return {
            **state,
            "candidate_sql": None,
            "sql_generated_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    """Test SQL generation node"""
    import sys

    print("=== SQL Generation Node Test ===\n")

    # Test cases
    test_questions = [
        "查询所有客户",
        "统计每个城市的客户数量",
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
            "sql_generated_at": None
        }

        result = generate_sql_node(test_state)

        print(f"\n✓ SQL Generated:")
        print(f"  {result.get('candidate_sql')}")

    print(f"\n{'='*60}")
    print("Test Complete!")
    print(f"{'='*60}")
