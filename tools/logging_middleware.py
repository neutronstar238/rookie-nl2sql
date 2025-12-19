"""
Logging middleware for NL2SQL graph nodes.
M11: Automatic logging decorators and helpers for graph nodes.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
import traceback
from functools import wraps
from typing import Callable, Dict, Any
from graphs.state import NL2SQLState
from tools.logger import get_logger, NodeType


def log_node(node_type: NodeType):
    """
    Decorator to automatically log node execution.
    
    Usage:
        @log_node(NodeType.GENERATE_SQL)
        def generate_sql_node(state: NL2SQLState) -> NL2SQLState:
            # ...your node logic...
            return state
    
    Args:
        node_type: Type of the node being decorated
    
    Returns:
        Decorated function with automatic logging
    """
    def decorator(func: Callable[[NL2SQLState], NL2SQLState]) -> Callable:
        @wraps(func)
        def wrapper(state: NL2SQLState) -> NL2SQLState:
            logger = get_logger()
            trace_id = state.get('trace_id')
            
            if not trace_id:
                # If no trace_id, generate one
                trace_id = logger.generate_trace_id()
                state['trace_id'] = trace_id
            
            # Prepare input data (sanitize for logging)
            input_data = {
                "question": state.get('question'),
                "session_id": state.get('session_id'),
                "has_sql": state.get('candidate_sql') is not None,
                "has_schema": state.get('schema') is not None
            }
            
            # Execute node
            start_time = time.time()
            success = True
            error_msg = None
            
            try:
                result_state = func(state)
            except Exception as e:
                success = False
                error_msg = str(e)
                stack_trace = traceback.format_exc()
                
                # Log error
                logger.log_error(
                    trace_id=trace_id,
                    node_type=node_type,
                    error_type=type(e).__name__,
                    error_message=error_msg,
                    stack_trace=stack_trace,
                    context={"state_keys": list(state.keys())}
                )
                
                # Re-raise exception
                raise
            finally:
                execution_time = time.time() - start_time
                
                # Prepare output data
                if success:
                    output_data = _extract_node_output(node_type, result_state)
                else:
                    output_data = {"error": error_msg}
                
                # Log node execution
                logger.log_node_execution(
                    trace_id=trace_id,
                    node_type=node_type,
                    input_data=input_data,
                    output_data=output_data,
                    execution_time=execution_time,
                    success=success,
                    error=error_msg
                )
                
                # Update state timings
                if success:
                    if 'node_timings' not in result_state or result_state['node_timings'] is None:
                        result_state['node_timings'] = {}
                    result_state['node_timings'][node_type.value] = execution_time
            
            return result_state
        
        return wrapper
    return decorator


def _extract_node_output(node_type: NodeType, state: NL2SQLState) -> Dict[str, Any]:
    """
    Extract relevant output data from state based on node type.
    
    Args:
        node_type: Type of node
        state: Current state
        
    Returns:
        Dictionary of relevant output data
    """
    output = {}
    
    if node_type == NodeType.PARSE_INTENT:
        output['intent'] = state.get('intent')
    
    elif node_type == NodeType.CLARIFY_INTENT:
        output['needs_clarification'] = state.get('clarification_needed')
        output['ambiguity_score'] = state.get('ambiguity_score')
    
    elif node_type == NodeType.RAG_RETRIEVAL:
        rag = state.get('rag_evidence', {})
        output['has_evidence'] = rag.get('has_evidence', False)
        output['recognized_terms'] = len(rag.get('recognized_terms', []))
        output['similar_examples'] = len(rag.get('similar_examples', []))
    
    elif node_type == NodeType.MATCH_JOIN:
        output['join_complexity'] = state.get('join_complexity')
        output['has_templates'] = len(state.get('suggested_templates', [])) > 0
    
    elif node_type == NodeType.SCHEMA_INGESTION:
        schema = state.get('schema', {})
        output['tables_loaded'] = len(schema.get('tables', []))
    
    elif node_type == NodeType.GENERATE_SQL:
        output['sql_generated'] = state.get('candidate_sql') is not None
        sql = state.get('candidate_sql', '')
        output['sql_length'] = len(sql) if sql else 0
    
    elif node_type == NodeType.VALIDATE_SQL:
        validation = state.get('validation_result', {})
        output['valid'] = validation.get('valid', False)
        output['errors'] = validation.get('errors', [])
    
    elif node_type == NodeType.SANDBOX_CHECK:
        sandbox = state.get('sandbox_check', {})
        output['allowed'] = sandbox.get('allowed', False)
        output['risk_level'] = sandbox.get('risk_level')
    
    elif node_type == NodeType.EXECUTE_SQL:
        execution = state.get('execution_result', {})
        output['success'] = execution.get('ok', False)
        output['row_count'] = execution.get('row_count', 0)
    
    elif node_type == NodeType.ANSWER_BUILDER:
        output['answer_generated'] = state.get('answer') is not None
        answer = state.get('answer', '')
        output['answer_length'] = len(answer) if answer else 0
    
    elif node_type == NodeType.ECHO:
        output['session_id'] = state.get('session_id')
        output['has_answer'] = state.get('answer') is not None
    
    return output


class TraceContext:
    """
    Context manager for trace lifecycle.
    
    Usage:
        with TraceContext(question="显示所有专辑") as trace_id:
            # Run graph
            result = graph.invoke(state)
    """
    
    def __init__(self, question: str, session_id: str = None, metadata: Dict = None):
        """
        Initialize trace context.
        
        Args:
            question: User's question
            session_id: Optional session ID
            metadata: Optional metadata
        """
        self.question = question
        self.session_id = session_id
        self.metadata = metadata or {}
        self.trace_id = None
        self.start_time = None
        self.logger = get_logger()
    
    def __enter__(self) -> str:
        """Start trace"""
        self.trace_id = self.logger.generate_trace_id()
        self.start_time = time.time()
        
        self.logger.log_trace_start(
            trace_id=self.trace_id,
            question=self.question,
            session_id=self.session_id,
            metadata=self.metadata
        )
        
        return self.trace_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End trace"""
        total_time = time.time() - self.start_time
        success = exc_type is None
        
        error_msg = None
        if not success:
            error_msg = f"{exc_type.__name__}: {exc_val}"
        
        self.logger.log_trace_end(
            trace_id=self.trace_id,
            success=success,
            total_time=total_time,
            error=error_msg
        )
        
        # Don't suppress exceptions
        return False


if __name__ == "__main__":
    """Demo logging middleware"""
    from tools.logger import NodeType
    
    print("=" * 70)
    print("Logging Middleware Demo")
    print("=" * 70)
    
    # Demo 1: Using decorator
    @log_node(NodeType.GENERATE_SQL)
    def generate_sql_node(state: NL2SQLState) -> NL2SQLState:
        """Simulated SQL generation node"""
        time.sleep(0.2)  # Simulate processing
        state['candidate_sql'] = "SELECT * FROM Album"
        state['sql_generated_at'] = "2025-12-18T13:00:00"
        return state
    
    print("\n1. Testing @log_node decorator:")
    test_state: NL2SQLState = {
        'question': "显示所有专辑",
        'session_id': "demo_001",
        'trace_id': None,  # Will be auto-generated
        'timestamp': None,
        'intent': None,
        'candidate_sql': None,
        'sql_generated_at': None,
        'execution_result': None,
        'executed_at': None,
        'schema': None,
        'schema_loaded_at': None,
        'validation_result': None,
        'validated_at': None,
        'sandbox_check': None,
        'sandbox_checked_at': None,
        'rag_evidence': None,
        'rag_retrieved_at': None,
        'clarification_needed': None,
        'clarification_questions': None,
        'ambiguity_score': None,
        'normalized_question': None,
        'clarified_at': None,
        'join_complexity': None,
        'suggested_templates': None,
        'template_matched_at': None,
        'answer': None,
        'answer_generated_at': None,
        'node_timings': None,
        'total_llm_tokens': None
    }
    
    result_state = generate_sql_node(test_state)
    print(f"   ✓ Trace ID: {result_state['trace_id']}")
    print(f"   ✓ SQL Generated: {result_state['candidate_sql']}")
    print(f"   ✓ Node Timing: {result_state['node_timings']['generate_sql']:.2f}s")
    
    # Demo 2: Using TraceContext
    print("\n2. Testing TraceContext:")
    with TraceContext(question="有多少首歌曲？", session_id="demo_002") as trace_id:
        print(f"   ✓ Trace started: {trace_id}")
        time.sleep(0.3)  # Simulate processing
        print(f"   ✓ Processing complete")
    
    print("\n3. Logs saved to: logs/")
    print("=" * 70)
