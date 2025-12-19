"""
Schema Ingestion Node for NL2SQL system.
M3: Loads and formats database schema for SQL generation.
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from graphs.state import NL2SQLState
from tools.db import db_client
from tools.schema_formatter import format_schema_for_llm


def schema_ingestion_node(state: NL2SQLState) -> NL2SQLState:
    """
    Load and format database schema for SQL generation.
    
    M3: Retrieves complete database schema and formats it for LLM consumption.
    
    Args:
        state: Current NL2SQL state
    
    Returns:
        Updated state with schema information
    """
    print(f"\n=== Schema Ingestion Node ===")
    
    try:
        # Get all table schemas from database
        schemas = db_client.get_all_schemas()
        
        if not schemas:
            print("⚠️  Warning: No schemas found in database")
            return {
                **state,
                "schema": None,
                "schema_loaded_at": datetime.now().isoformat()
            }
        
        print(f"✓ Loaded {len(schemas)} table schemas")
        
        # Format schema for LLM
        formatted_schema = format_schema_for_llm(schemas, include_samples=True)
        
        # Create schema object
        schema_info = {
            "tables": schemas,
            "formatted": formatted_schema,
            "table_count": len(schemas),
            "table_names": [s["table_name"] for s in schemas]
        }
        
        # Print summary
        print(f"Tables: {', '.join(schema_info['table_names'])}")
        
        return {
            **state,
            "schema": schema_info,
            "schema_loaded_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"✗ Error loading schema: {e}")
        return {
            **state,
            "schema": None,
            "schema_loaded_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    """Test schema ingestion node"""
    print("=== Schema Ingestion Node Test ===\n")
    
    # Test state
    test_state: NL2SQLState = {
        "question": "Show all albums",
        "session_id": "test-123",
        "timestamp": None,
        "intent": None,
        "candidate_sql": None,
        "sql_generated_at": None,
        "execution_result": None,
        "executed_at": None,
        "schema": None,
        "schema_loaded_at": None
    }
    
    # Run node
    result = schema_ingestion_node(test_state)
    
    # Print results
    print("\n" + "="*70)
    print("Schema Loading Results:")
    print("="*70)
    
    schema = result.get("schema")
    if schema:
        print(f"✓ Schema loaded successfully")
        print(f"  Tables: {schema['table_count']}")
        print(f"  Table names: {', '.join(schema['table_names'])}")
        print(f"\nFormatted Schema Preview (first 500 chars):")
        print("-" * 70)
        print(schema['formatted'][:500] + "...")
    else:
        print("✗ Schema loading failed")
    
    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70)
