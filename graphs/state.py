"""
State definition for NL2SQL LangGraph system.
"""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class NL2SQLState(TypedDict):
    """
    Base state for the NL2SQL graph.

    This state will be extended in future modules with:
    - normalized_question (M7)
    - schema (M3)
    - rag_evidence (M6)
    - candidate_sql (M1) ✓ Added
    - validation (M4)
    - execution (M2)
    - answer (M9)
    - trace (M11)
    """
    # User input
    question: str

    # Metadata
    timestamp: Optional[str]
    session_id: Optional[str]
    trace_id: Optional[str]  # M11: Trace ID for request tracking

    # Intent parsing (M0 baseline)
    intent: Optional[Dict[str, Any]]

    # SQL Generation (M1)
    candidate_sql: Optional[str]
    sql_generated_at: Optional[str]

    # SQL Execution (M2)
    execution_result: Optional[Dict[str, Any]]
    executed_at: Optional[str]

    # Schema Ingestion (M3)
    schema: Optional[Dict[str, Any]]
    schema_loaded_at: Optional[str]

    # SQL Validation (M4)
    validation_result: Optional[Dict[str, Any]]
    validated_at: Optional[str]

    # Execution Sandbox (M5)
    sandbox_check: Optional[Dict[str, Any]]
    sandbox_checked_at: Optional[str]

    # RAG Evidence (M6)
    rag_evidence: Optional[Dict[str, Any]]
    rag_retrieved_at: Optional[str]

    # Dialog Clarification (M7)
    clarification_needed: Optional[bool]
    clarification_questions: Optional[List[str]]
    ambiguity_score: Optional[float]
    normalized_question: Optional[str]
    clarified_at: Optional[str]

    # Join Few-Shot (M8)
    join_complexity: Optional[str]
    suggested_templates: Optional[List[Dict[str, Any]]]
    template_matched_at: Optional[str]

    # Answer Generation (M9)
    answer: Optional[str]
    answer_generated_at: Optional[str]

    # Observability (M11)
    node_timings: Optional[Dict[str, float]]  # Node execution times
    total_llm_tokens: Optional[int]  # Total LLM tokens used
