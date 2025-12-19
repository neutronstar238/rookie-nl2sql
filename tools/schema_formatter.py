"""
Schema formatting utilities for NL2SQL system.
M3: Formats database schema for LLM consumption.
"""
from typing import Dict, Any, List
from tools.db import db_client


def format_schema_for_llm(schemas: List[Dict[str, Any]], include_samples: bool = True) -> str:
    """
    Format database schema information for LLM prompt.
    
    Args:
        schemas: List of table schema dictionaries
        include_samples: Whether to include sample values for each table
    
    Returns:
        Formatted schema string for LLM
    """
    if not schemas:
        return "No schema available."
    
    schema_parts = []
    schema_parts.append("=== DATABASE SCHEMA ===\n")
    
    for schema in schemas:
        table_name = schema.get("table_name", "Unknown")
        columns = schema.get("columns", [])
        
        if not columns:
            continue
        
        # Format table header
        schema_parts.append(f"\n## Table: {table_name}")
        
        # Format columns
        col_strs = []
        pk_cols = []
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "")
            is_pk = col.get("primary_key", False)
            is_nn = col.get("not_null", False)
            
            col_str = f"  - {col_name} ({col_type})"
            if is_pk:
                col_str += " [PRIMARY KEY]"
                pk_cols.append(col_name)
            if is_nn and not is_pk:
                col_str += " [NOT NULL]"
            
            col_strs.append(col_str)
        
        schema_parts.append("Columns:")
        schema_parts.extend(col_strs)
        
        # Add sample data if requested
        if include_samples:
            try:
                sample_result = db_client.query(f"SELECT * FROM {table_name} LIMIT 3")
                if sample_result["ok"] and sample_result["rows"]:
                    schema_parts.append(f"\nSample rows (first 3):")
                    for i, row in enumerate(sample_result["rows"], 1):
                        # Format row compactly
                        row_str = ", ".join([f"{k}={v}" for k, v in list(row.items())[:3]])
                        if len(row) > 3:
                            row_str += "..."
                        schema_parts.append(f"  {i}. {row_str}")
            except:
                pass  # Skip samples if query fails
        
        schema_parts.append("")  # Empty line between tables
    
    return "\n".join(schema_parts)


def format_schema_compact(schemas: List[Dict[str, Any]]) -> str:
    """
    Format database schema in compact format (one line per table).
    Useful for shorter prompts.
    
    Args:
        schemas: List of table schema dictionaries
    
    Returns:
        Compact schema string
    """
    if not schemas:
        return "No schema available."
    
    lines = []
    for schema in schemas:
        table_name = schema.get("table_name", "Unknown")
        columns = schema.get("columns", [])
        
        if not columns:
            continue
        
        # Get column names and types
        col_parts = []
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "")
            is_pk = col.get("primary_key", False)
            
            if is_pk:
                col_parts.append(f"{col_name}:{col_type}[PK]")
            else:
                col_parts.append(f"{col_name}:{col_type}")
        
        # Format: TableName (col1:type, col2:type, ...)
        line = f"{table_name} ({', '.join(col_parts)})"
        lines.append(line)
    
    return "\n".join(lines)


def get_table_relationships(schemas: List[Dict[str, Any]]) -> str:
    """
    Detect and format foreign key relationships between tables.
    M3: Basic heuristic-based detection (looks for *Id columns).
    M6: Could be enhanced with actual FK constraints.
    
    Args:
        schemas: List of table schema dictionaries
    
    Returns:
        Formatted relationship string
    """
    relationships = []
    
    # Build a map of table names for quick lookup
    table_names = {s["table_name"] for s in schemas}
    
    for schema in schemas:
        table_name = schema.get("table_name", "")
        columns = schema.get("columns", [])
        
        for col in columns:
            col_name = col.get("name", "")
            
            # Heuristic: column name ends with "Id" and matches a table name
            if col_name.endswith("Id") and col_name != f"{table_name}Id":
                # Try to find matching table
                potential_table = col_name[:-2]  # Remove "Id"
                
                if potential_table in table_names:
                    relationships.append(f"{table_name}.{col_name} -> {potential_table}.{potential_table}Id")
    
    if relationships:
        return "Relationships:\n" + "\n".join([f"  - {rel}" for rel in relationships])
    else:
        return ""


def format_schema_with_stats(schemas: List[Dict[str, Any]]) -> str:
    """
    Format schema with table statistics (row counts).
    
    Args:
        schemas: List of table schema dictionaries
    
    Returns:
        Schema string with statistics
    """
    parts = []
    parts.append("=== DATABASE OVERVIEW ===\n")
    
    total_tables = len(schemas)
    parts.append(f"Total tables: {total_tables}\n")
    
    for schema in schemas:
        table_name = schema.get("table_name", "")
        columns = schema.get("columns", [])
        
        # Get row count
        try:
            count_result = db_client.query(f"SELECT COUNT(*) as cnt FROM {table_name}")
            row_count = count_result["rows"][0]["cnt"] if count_result["ok"] else "?"
        except:
            row_count = "?"
        
        parts.append(f"- {table_name}: {len(columns)} columns, {row_count} rows")
    
    return "\n".join(parts)


if __name__ == "__main__":
    """Test schema formatting"""
    print("=== Schema Formatter Test ===\n")
    
    # Get all schemas
    schemas = db_client.get_all_schemas()
    print(f"Loaded {len(schemas)} table schemas\n")
    
    # Test 1: Full format with samples
    print("1. Full format with samples:")
    print("=" * 70)
    print(format_schema_for_llm(schemas, include_samples=True))
    print()
    
    # Test 2: Compact format
    print("\n2. Compact format:")
    print("=" * 70)
    print(format_schema_compact(schemas))
    print()
    
    # Test 3: Relationships
    print("\n3. Table relationships:")
    print("=" * 70)
    print(get_table_relationships(schemas))
    print()
    
    # Test 4: Statistics
    print("\n4. Schema with statistics:")
    print("=" * 70)
    print(format_schema_with_stats(schemas))
    print()
    
    print("=== Test Complete ===")
