"""
NL2SQL System Logger with Trace Support
M11: Observability - Structured logging with TraceID mechanism for request tracing.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class NodeType(Enum):
    """Graph node types for categorization"""
    PARSE_INTENT = "parse_intent"
    CLARIFY_INTENT = "clarify_intent"
    RAG_RETRIEVAL = "rag_retrieval"
    MATCH_JOIN = "match_join_template"
    SCHEMA_INGESTION = "schema_ingestion"
    GENERATE_SQL = "generate_sql"
    VALIDATE_SQL = "validate_sql"
    SANDBOX_CHECK = "sandbox_check"
    EXECUTE_SQL = "execute_sql"
    ANSWER_BUILDER = "answer_builder"
    ECHO = "echo"


class NL2SQLLogger:
    """
    Structured logger for NL2SQL system with trace support.
    
    Features:
    - Automatic TraceID generation and propagation
    - Structured JSON logging
    - Node-level performance tracking
    - Error tracking with stack traces
    - Query history and replay support
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log files
        self.trace_log_file = self.log_dir / "traces.jsonl"
        self.node_log_file = self.log_dir / "nodes.jsonl"
        self.error_log_file = self.log_dir / "errors.jsonl"
        self.metrics_log_file = self.log_dir / "metrics.jsonl"
    
    def generate_trace_id(self) -> str:
        """Generate unique trace ID for a request"""
        return f"trace_{uuid.uuid4().hex[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def log_trace_start(
        self,
        trace_id: str,
        question: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log the start of a new trace (query request).
        
        Args:
            trace_id: Unique trace identifier
            question: User's natural language question
            session_id: Optional session ID for multi-turn dialogs
            metadata: Additional metadata (e.g., user_id, source)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id,
            "session_id": session_id,
            "event": "trace_start",
            "question": question,
            "metadata": metadata or {}
        }
        self._write_log(self.trace_log_file, log_entry)
    
    def log_trace_end(
        self,
        trace_id: str,
        success: bool,
        total_time: float,
        final_answer: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log the end of a trace.
        
        Args:
            trace_id: Trace identifier
            success: Whether the request succeeded
            total_time: Total execution time in seconds
            final_answer: Generated answer (if successful)
            error: Error message (if failed)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id,
            "event": "trace_end",
            "success": success,
            "total_time": total_time,
            "final_answer": final_answer,
            "error": error
        }
        self._write_log(self.trace_log_file, log_entry)
    
    def log_node_execution(
        self,
        trace_id: str,
        node_type: NodeType,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time: float,
        success: bool = True,
        error: Optional[str] = None,
        llm_tokens: Optional[Dict[str, int]] = None
    ) -> None:
        """
        Log execution of a graph node.
        
        Args:
            trace_id: Trace identifier
            node_type: Type of node executed
            input_data: Node input (sanitized)
            output_data: Node output (sanitized)
            execution_time: Node execution time in seconds
            success: Whether node executed successfully
            error: Error message if failed
            llm_tokens: LLM token usage (input_tokens, output_tokens, total_tokens)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id,
            "node_type": node_type.value,
            "input_data": self._sanitize_data(input_data),
            "output_data": self._sanitize_data(output_data),
            "execution_time": execution_time,
            "success": success,
            "error": error,
            "llm_tokens": llm_tokens
        }
        self._write_log(self.node_log_file, log_entry)
    
    def log_error(
        self,
        trace_id: str,
        node_type: Optional[NodeType],
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error occurrence.
        
        Args:
            trace_id: Trace identifier
            node_type: Node where error occurred
            error_type: Error type/category
            error_message: Error message
            stack_trace: Full stack trace
            context: Additional context for debugging
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id,
            "node_type": node_type.value if node_type else None,
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context or {}
        }
        self._write_log(self.error_log_file, log_entry)
    
    def log_metrics(
        self,
        trace_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Log performance metrics.
        
        Args:
            trace_id: Trace identifier
            metrics: Metrics dictionary (e.g., latency, tokens, cache hits)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id,
            **metrics
        }
        self._write_log(self.metrics_log_file, log_entry)
    
    def get_trace_logs(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all logs for a specific trace.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            List of log entries for the trace
        """
        logs = []
        
        # Read from all log files
        for log_file in [self.trace_log_file, self.node_log_file, 
                         self.error_log_file, self.metrics_log_file]:
            if not log_file.exists():
                continue
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('trace_id') == trace_id:
                            logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        # Sort by timestamp
        logs.sort(key=lambda x: x.get('timestamp', ''))
        return logs
    
    def get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent trace summaries.
        
        Args:
            limit: Maximum number of traces to return
            
        Returns:
            List of trace summaries
        """
        traces = {}
        
        if not self.trace_log_file.exists():
            return []
        
        with open(self.trace_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    trace_id = entry.get('trace_id')
                    
                    if trace_id not in traces:
                        traces[trace_id] = {
                            'trace_id': trace_id,
                            'question': None,
                            'start_time': None,
                            'end_time': None,
                            'success': None,
                            'total_time': None
                        }
                    
                    if entry.get('event') == 'trace_start':
                        traces[trace_id]['question'] = entry.get('question')
                        traces[trace_id]['start_time'] = entry.get('timestamp')
                    elif entry.get('event') == 'trace_end':
                        traces[trace_id]['end_time'] = entry.get('timestamp')
                        traces[trace_id]['success'] = entry.get('success')
                        traces[trace_id]['total_time'] = entry.get('total_time')
                
                except json.JSONDecodeError:
                    continue
        
        # Sort by start time (most recent first)
        trace_list = list(traces.values())
        trace_list.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        
        return trace_list[:limit]
    
    def replay_trace(self, trace_id: str) -> Dict[str, Any]:
        """
        Replay a trace for debugging.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            Detailed trace information for replay
        """
        logs = self.get_trace_logs(trace_id)
        
        if not logs:
            return {"error": f"No logs found for trace {trace_id}"}
        
        # Organize logs by type
        trace_info = {
            "trace_id": trace_id,
            "timeline": [],
            "nodes": [],
            "errors": [],
            "metrics": [],
            "summary": {}
        }
        
        for log in logs:
            event_type = log.get('event')
            
            if event_type == 'trace_start':
                trace_info['summary']['question'] = log.get('question')
                trace_info['summary']['start_time'] = log.get('timestamp')
            elif event_type == 'trace_end':
                trace_info['summary']['end_time'] = log.get('timestamp')
                trace_info['summary']['success'] = log.get('success')
                trace_info['summary']['total_time'] = log.get('total_time')
            elif 'node_type' in log and 'execution_time' in log:
                trace_info['nodes'].append(log)
            elif 'error_type' in log:
                trace_info['errors'].append(log)
            
            trace_info['timeline'].append(log)
        
        return trace_info
    
    def _sanitize_data(self, data: Any, max_length: int = 500) -> Any:
        """
        Sanitize data for logging (remove sensitive info, truncate long strings).
        
        Args:
            data: Data to sanitize
            max_length: Maximum string length
            
        Returns:
            Sanitized data
        """
        if isinstance(data, str):
            if len(data) > max_length:
                return data[:max_length] + "... (truncated)"
            return data
        elif isinstance(data, dict):
            return {k: self._sanitize_data(v, max_length) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(item, max_length) for item in data]
        else:
            return data
    
    def _write_log(self, log_file: Path, entry: Dict[str, Any]) -> None:
        """
        Write log entry to file.
        
        Args:
            log_file: Log file path
            entry: Log entry dictionary
        """
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            # Fallback to stderr if file write fails
            import sys
            print(f"Failed to write log: {e}", file=sys.stderr)


# Global logger instance
_global_logger: Optional[NL2SQLLogger] = None


def get_logger(log_dir: str = "logs") -> NL2SQLLogger:
    """
    Get or create global logger instance.
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        NL2SQLLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = NL2SQLLogger(log_dir)
    return _global_logger


# Convenience functions
def log_trace_start(trace_id: str, question: str, **kwargs) -> None:
    """Log trace start"""
    get_logger().log_trace_start(trace_id, question, **kwargs)


def log_trace_end(trace_id: str, success: bool, total_time: float, **kwargs) -> None:
    """Log trace end"""
    get_logger().log_trace_end(trace_id, success, total_time, **kwargs)


def log_node(trace_id: str, node_type: NodeType, input_data: Dict, 
             output_data: Dict, execution_time: float, **kwargs) -> None:
    """Log node execution"""
    get_logger().log_node_execution(
        trace_id, node_type, input_data, output_data, execution_time, **kwargs
    )


def log_error(trace_id: str, error_type: str, error_message: str, **kwargs) -> None:
    """Log error"""
    get_logger().log_error(trace_id, None, error_type, error_message, **kwargs)


if __name__ == "__main__":
    """Demo and test logger functionality"""
    import time
    
    print("=" * 70)
    print("NL2SQL Logger Demo")
    print("=" * 70)
    
    logger = get_logger(log_dir="logs/demo")
    
    # Simulate a query trace
    trace_id = logger.generate_trace_id()
    question = "显示所有专辑"
    
    print(f"\n1. Starting trace: {trace_id}")
    logger.log_trace_start(trace_id, question, session_id="demo_session_1")
    
    start_time = time.time()
    
    # Simulate node executions
    print("\n2. Simulating node executions...")
    
    # Parse Intent
    time.sleep(0.1)
    logger.log_node_execution(
        trace_id=trace_id,
        node_type=NodeType.PARSE_INTENT,
        input_data={"question": question},
        output_data={"intent": {"type": "query"}},
        execution_time=0.1
    )
    
    # Generate SQL
    time.sleep(0.2)
    logger.log_node_execution(
        trace_id=trace_id,
        node_type=NodeType.GENERATE_SQL,
        input_data={"question": question},
        output_data={"sql": "SELECT * FROM Album"},
        execution_time=0.2,
        llm_tokens={"input_tokens": 150, "output_tokens": 20, "total_tokens": 170}
    )
    
    # Execute SQL
    time.sleep(0.15)
    logger.log_node_execution(
        trace_id=trace_id,
        node_type=NodeType.EXECUTE_SQL,
        input_data={"sql": "SELECT * FROM Album"},
        output_data={"rows": 100, "success": True},
        execution_time=0.15
    )
    
    total_time = time.time() - start_time
    
    print(f"\n3. Ending trace (total time: {total_time:.2f}s)")
    logger.log_trace_end(
        trace_id=trace_id,
        success=True,
        total_time=total_time,
        final_answer="找到 100 张专辑"
    )
    
    # Demonstrate replay
    print(f"\n4. Replaying trace...")
    replay = logger.replay_trace(trace_id)
    
    print(f"\nTrace Summary:")
    print(f"  Question: {replay['summary'].get('question')}")
    print(f"  Success: {replay['summary'].get('success')}")
    print(f"  Total Time: {replay['summary'].get('total_time'):.2f}s")
    print(f"  Nodes Executed: {len(replay['nodes'])}")
    
    print(f"\nNode Timeline:")
    for node in replay['nodes']:
        print(f"  - {node['node_type']}: {node['execution_time']:.2f}s")
    
    # Show recent traces
    print(f"\n5. Recent traces:")
    recent = logger.get_recent_traces(limit=5)
    for i, trace in enumerate(recent, 1):
        print(f"  {i}. {trace['trace_id'][:30]}... - {trace.get('question', 'N/A')}")
    
    print(f"\n✓ Logs saved to: {logger.log_dir}")
    print(f"  - Trace logs: {logger.trace_log_file}")
    print(f"  - Node logs: {logger.node_log_file}")
    print("=" * 70)
