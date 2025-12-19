"""
Log Analyzer for NL2SQL System
M11: Tools for analyzing logs, debugging failures, and generating insights.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from tools.logger import get_logger


class LogAnalyzer:
    """
    Analyze NL2SQL system logs for insights and debugging.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize log analyzer.
        
        Args:
            log_dir: Directory containing log files
        """
        self.logger = get_logger(log_dir)
    
    def get_failed_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get traces that failed.
        
        Args:
            limit: Maximum number of failed traces to return
            
        Returns:
            List of failed trace summaries
        """
        failed = []
        
        if not self.logger.trace_log_file.exists():
            return []
        
        with open(self.logger.trace_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get('event') == 'trace_end' and not entry.get('success'):
                        trace_id = entry.get('trace_id')
                        # Get full trace details
                        trace_logs = self.logger.get_trace_logs(trace_id)
                        
                        # Find question
                        question = None
                        for log in trace_logs:
                            if log.get('event') == 'trace_start':
                                question = log.get('question')
                                break
                        
                        failed.append({
                            'trace_id': trace_id,
                            'question': question,
                            'error': entry.get('error'),
                            'timestamp': entry.get('timestamp'),
                            'total_time': entry.get('total_time')
                        })
                        
                        if len(failed) >= limit:
                            break
                
                except json.JSONDecodeError:
                    continue
        
        return failed
    
    def get_node_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance statistics for each node type.
        
        Returns:
            Dictionary with node stats (avg_time, min_time, max_time, count)
        """
        node_times = defaultdict(list)
        
        if not self.logger.node_log_file.exists():
            return {}
        
        with open(self.logger.node_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    node_type = entry.get('node_type')
                    execution_time = entry.get('execution_time')
                    
                    if node_type and execution_time is not None:
                        node_times[node_type].append(execution_time)
                
                except json.JSONDecodeError:
                    continue
        
        # Calculate statistics
        stats = {}
        for node_type, times in node_times.items():
            if times:
                stats[node_type] = {
                    'count': len(times),
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'total_time': sum(times)
                }
        
        return stats
    
    def get_error_distribution(self) -> Dict[str, int]:
        """
        Get distribution of error types.
        
        Returns:
            Dictionary mapping error types to counts
        """
        error_types = Counter()
        
        if not self.logger.error_log_file.exists():
            return {}
        
        with open(self.logger.error_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    error_type = entry.get('error_type')
                    if error_type:
                        error_types[error_type] += 1
                
                except json.JSONDecodeError:
                    continue
        
        return dict(error_types)
    
    def get_slow_queries(self, threshold: float = 10.0, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get slow queries (above threshold).
        
        Args:
            threshold: Time threshold in seconds
            limit: Maximum number of queries to return
            
        Returns:
            List of slow query details
        """
        slow_queries = []
        
        if not self.logger.trace_log_file.exists():
            return []
        
        traces = {}
        with open(self.logger.trace_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    trace_id = entry.get('trace_id')
                    
                    if trace_id not in traces:
                        traces[trace_id] = {}
                    
                    if entry.get('event') == 'trace_start':
                        traces[trace_id]['question'] = entry.get('question')
                        traces[trace_id]['start_time'] = entry.get('timestamp')
                    elif entry.get('event') == 'trace_end':
                        total_time = entry.get('total_time', 0)
                        if total_time >= threshold:
                            slow_queries.append({
                                'trace_id': trace_id,
                                'question': traces[trace_id].get('question'),
                                'total_time': total_time,
                                'timestamp': entry.get('timestamp'),
                                'success': entry.get('success')
                            })
                
                except json.JSONDecodeError:
                    continue
        
        # Sort by time (slowest first)
        slow_queries.sort(key=lambda x: x['total_time'], reverse=True)
        return slow_queries[:limit]
    
    def analyze_trace_bottlenecks(self, trace_id: str) -> Dict[str, Any]:
        """
        Analyze a trace to identify bottlenecks.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            Analysis with bottleneck information
        """
        logs = self.logger.get_trace_logs(trace_id)
        
        if not logs:
            return {"error": f"No logs found for trace {trace_id}"}
        
        # Extract node timings
        node_timings = []
        for log in logs:
            if 'node_type' in log and 'execution_time' in log:
                node_timings.append({
                    'node': log['node_type'],
                    'time': log['execution_time'],
                    'timestamp': log['timestamp']
                })
        
        if not node_timings:
            return {"error": "No node timing data found"}
        
        # Calculate total time
        total_time = sum(n['time'] for n in node_timings)
        
        # Find slowest nodes
        slowest = sorted(node_timings, key=lambda x: x['time'], reverse=True)
        
        # Calculate percentages
        for node in slowest:
            node['percentage'] = (node['time'] / total_time * 100) if total_time > 0 else 0
        
        return {
            'trace_id': trace_id,
            'total_time': total_time,
            'node_count': len(node_timings),
            'slowest_nodes': slowest[:5],  # Top 5 slowest
            'node_breakdown': node_timings
        }
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary report.
        
        Returns:
            Summary report with key metrics
        """
        # Get recent traces
        recent_traces = self.logger.get_recent_traces(limit=100)
        
        # Count successful/failed
        total = len(recent_traces)
        successful = sum(1 for t in recent_traces if t.get('success'))
        failed = total - successful
        
        # Calculate average time
        times = [t.get('total_time', 0) for t in recent_traces if t.get('total_time')]
        avg_time = sum(times) / len(times) if times else 0
        
        return {
            'period': 'last_100_traces',
            'total_traces': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'avg_response_time': avg_time,
            'node_performance': self.get_node_performance_stats(),
            'error_distribution': self.get_error_distribution(),
            'slowest_queries': self.get_slow_queries(threshold=5.0, limit=5)
        }
    
    def print_summary_report(self) -> None:
        """Print summary report to console"""
        report = self.generate_summary_report()
        
        print("=" * 70)
        print("NL2SQL SYSTEM SUMMARY REPORT")
        print("=" * 70)
        
        print(f"\n📊 Overview ({report['period']})")
        print(f"  Total Traces: {report['total_traces']}")
        print(f"  Successful: {report['successful']} ({report['success_rate']:.1f}%)")
        print(f"  Failed: {report['failed']}")
        print(f"  Avg Response Time: {report['avg_response_time']:.2f}s")
        
        print(f"\n⚡ Node Performance")
        node_perf = report['node_performance']
        if node_perf:
            sorted_nodes = sorted(
                node_perf.items(), 
                key=lambda x: x[1]['avg_time'], 
                reverse=True
            )
            for node, stats in sorted_nodes[:5]:
                print(f"  {node:20s}: {stats['avg_time']:.2f}s avg "
                      f"({stats['count']} executions)")
        else:
            print("  No node performance data available")
        
        print(f"\n❌ Error Distribution")
        errors = report['error_distribution']
        if errors:
            for error_type, count in errors.items():
                print(f"  {error_type}: {count}")
        else:
            print("  No errors recorded")
        
        print(f"\n🐌 Slowest Queries")
        slow = report['slowest_queries']
        if slow:
            for i, query in enumerate(slow, 1):
                q_text = query['question'][:50] + "..." if len(query.get('question', '')) > 50 else query.get('question', 'N/A')
                print(f"  {i}. {q_text}")
                print(f"     Time: {query['total_time']:.2f}s | Success: {query['success']}")
        else:
            print("  No slow queries found")
        
        print("=" * 70)


if __name__ == "__main__":
    """Demo log analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze NL2SQL logs")
    parser.add_argument("--log-dir", default="logs", help="Log directory")
    parser.add_argument("--trace-id", help="Analyze specific trace")
    parser.add_argument("--failed", action="store_true", help="Show failed traces")
    parser.add_argument("--slow", action="store_true", help="Show slow queries")
    parser.add_argument("--summary", action="store_true", help="Show summary report")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(log_dir=args.log_dir)
    
    if args.trace_id:
        # Analyze specific trace
        print(f"Analyzing trace: {args.trace_id}")
        bottlenecks = analyzer.analyze_trace_bottlenecks(args.trace_id)
        print(json.dumps(bottlenecks, indent=2, ensure_ascii=False))
    
    elif args.failed:
        # Show failed traces
        failed = analyzer.get_failed_traces(limit=10)
        print(f"\nFailed Traces ({len(failed)}):")
        for trace in failed:
            print(f"\nTrace ID: {trace['trace_id']}")
            print(f"  Question: {trace['question']}")
            print(f"  Error: {trace['error']}")
            print(f"  Time: {trace['timestamp']}")
    
    elif args.slow:
        # Show slow queries
        slow = analyzer.get_slow_queries(threshold=5.0, limit=10)
        print(f"\nSlow Queries ({len(slow)}):")
        for query in slow:
            print(f"\nTrace ID: {query['trace_id']}")
            print(f"  Question: {query['question']}")
            print(f"  Time: {query['total_time']:.2f}s")
            print(f"  Success: {query['success']}")
    
    else:
        # Default: show summary report
        analyzer.print_summary_report()
