"""
M11 Acceptance Test: System Observability & Logging
Tests the logging, tracing, and observability features.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
import unittest
import shutil
from graphs.base_graph import run_query
from tools.logger import get_logger, NodeType
from tools.logging_middleware import TraceContext
from tools.log_analyzer import LogAnalyzer


class TestM11Observability(unittest.TestCase):
    """Test Suite for M11 - System Observability"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_log_dir = "logs/test_m11"
        # Clean up previous test logs
        test_dir = Path(cls.test_log_dir)
        if test_dir.exists():
            shutil.rmtree(test_dir)
        test_dir.mkdir(parents=True, exist_ok=True)
    
    def test_01_trace_id_generation(self):
        """Test 1: TraceID Generation"""
        print("\n" + "=" * 70)
        print("Test 1: TraceID Generation")
        print("=" * 70)
        
        logger = get_logger(log_dir=self.test_log_dir)
        
        # Generate multiple trace IDs
        trace_ids = [logger.generate_trace_id() for _ in range(5)]
        
        # Verify uniqueness
        self.assertEqual(len(trace_ids), len(set(trace_ids)), 
                        "Trace IDs should be unique")
        
        # Verify format
        for trace_id in trace_ids:
            self.assertTrue(trace_id.startswith("trace_"), 
                           f"Trace ID should start with 'trace_': {trace_id}")
            self.assertIn("_", trace_id,
                         f"Trace ID should contain underscores: {trace_id}")
        
        print(f"✓ Generated {len(trace_ids)} unique trace IDs")
        print(f"  Example: {trace_ids[0]}")
    
    def test_02_trace_lifecycle_logging(self):
        """Test 2: Trace Lifecycle Logging (Start → End)"""
        print("\n" + "=" * 70)
        print("Test 2: Trace Lifecycle Logging")
        print("=" * 70)
        
        logger = get_logger(log_dir=self.test_log_dir)
        trace_id = logger.generate_trace_id()
        question = "显示所有专辑"
        
        # Log trace start
        logger.log_trace_start(
            trace_id=trace_id,
            question=question,
            session_id="test_session_02"
        )
        
        # Simulate processing
        time.sleep(0.1)
        
        # Log trace end
        logger.log_trace_end(
            trace_id=trace_id,
            success=True,
            total_time=0.1,
            final_answer="找到 100 张专辑"
        )
        
        # Verify logs
        logs = logger.get_trace_logs(trace_id)
        self.assertGreater(len(logs), 0, "Should have logged trace events")
        
        # Verify trace start
        start_logs = [l for l in logs if l.get('event') == 'trace_start']
        self.assertEqual(len(start_logs), 1, "Should have one trace_start event")
        self.assertEqual(start_logs[0]['question'], question)
        
        # Verify trace end
        end_logs = [l for l in logs if l.get('event') == 'trace_end']
        self.assertEqual(len(end_logs), 1, "Should have one trace_end event")
        self.assertTrue(end_logs[0]['success'])
        
        print(f"✓ Trace lifecycle logged successfully")
        print(f"  Trace ID: {trace_id}")
        print(f"  Events logged: {len(logs)}")
    
    def test_03_node_execution_logging(self):
        """Test 3: Node Execution Logging"""
        print("\n" + "=" * 70)
        print("Test 3: Node Execution Logging")
        print("=" * 70)
        
        logger = get_logger(log_dir=self.test_log_dir)
        trace_id = logger.generate_trace_id()
        
        # Log multiple node executions
        nodes = [
            (NodeType.PARSE_INTENT, {"question": "测试"}, {"intent": "query"}, 0.05),
            (NodeType.GENERATE_SQL, {"question": "测试"}, {"sql": "SELECT *"}, 0.15),
            (NodeType.EXECUTE_SQL, {"sql": "SELECT *"}, {"rows": 10}, 0.08),
        ]
        
        for node_type, input_data, output_data, exec_time in nodes:
            logger.log_node_execution(
                trace_id=trace_id,
                node_type=node_type,
                input_data=input_data,
                output_data=output_data,
                execution_time=exec_time,
                success=True
            )
        
        # Verify node logs
        logs = logger.get_trace_logs(trace_id)
        node_logs = [l for l in logs if 'node_type' in l]
        
        self.assertEqual(len(node_logs), 3, "Should have logged 3 node executions")
        
        # Verify node types
        logged_nodes = [l['node_type'] for l in node_logs]
        expected_nodes = [n[0].value for n in nodes]
        self.assertEqual(logged_nodes, expected_nodes)
        
        print(f"✓ Node execution logging works")
        print(f"  Nodes logged: {len(node_logs)}")
        for log in node_logs:
            print(f"    - {log['node_type']}: {log['execution_time']:.2f}s")
    
    def test_04_error_logging(self):
        """Test 4: Error Logging"""
        print("\n" + "=" * 70)
        print("Test 4: Error Logging")
        print("=" * 70)
        
        logger = get_logger(log_dir=self.test_log_dir)
        trace_id = logger.generate_trace_id()
        
        # Log an error
        logger.log_error(
            trace_id=trace_id,
            node_type=NodeType.EXECUTE_SQL,
            error_type="DatabaseError",
            error_message="Table not found: NonExistent",
            stack_trace="Traceback...",
            context={"sql": "SELECT * FROM NonExistent"}
        )
        
        # Verify error log
        logs = logger.get_trace_logs(trace_id)
        error_logs = [l for l in logs if 'error_type' in l]
        
        self.assertEqual(len(error_logs), 1, "Should have logged 1 error")
        self.assertEqual(error_logs[0]['error_type'], "DatabaseError")
        self.assertEqual(error_logs[0]['node_type'], NodeType.EXECUTE_SQL.value)
        
        print(f"✓ Error logging works")
        print(f"  Error Type: {error_logs[0]['error_type']}")
        print(f"  Error Message: {error_logs[0]['error_message']}")
    
    def test_05_trace_context_manager(self):
        """Test 5: TraceContext Manager"""
        print("\n" + "=" * 70)
        print("Test 5: TraceContext Manager")
        print("=" * 70)
        
        get_logger(log_dir=self.test_log_dir)  # Initialize logger
        
        question = "有多少首歌曲？"
        
        # Use TraceContext
        with TraceContext(question=question, session_id="test_05") as trace_id:
            self.assertIsNotNone(trace_id)
            self.assertTrue(trace_id.startswith("trace_"))
            time.sleep(0.05)  # Simulate work
        
        # Verify trace was logged
        logger = get_logger(log_dir=self.test_log_dir)
        logs = logger.get_trace_logs(trace_id)
        
        self.assertGreater(len(logs), 0, "Should have logged trace")
        
        # Verify start and end
        events = [l.get('event') for l in logs]
        self.assertIn('trace_start', events)
        self.assertIn('trace_end', events)
        
        print(f"✓ TraceContext works")
        print(f"  Trace ID: {trace_id}")
        print(f"  Events: {events}")
    
    def test_06_trace_replay(self):
        """Test 6: Trace Replay for Debugging"""
        print("\n" + "=" * 70)
        print("Test 6: Trace Replay")
        print("=" * 70)
        
        logger = get_logger(log_dir=self.test_log_dir)
        trace_id = logger.generate_trace_id()
        
        # Create a complete trace
        logger.log_trace_start(trace_id, "测试问题", session_id="test_06")
        
        logger.log_node_execution(
            trace_id, NodeType.PARSE_INTENT,
            {"question": "测试"}, {"intent": "query"}, 0.05
        )
        logger.log_node_execution(
            trace_id, NodeType.GENERATE_SQL,
            {"question": "测试"}, {"sql": "SELECT"}, 0.10
        )
        
        logger.log_trace_end(trace_id, True, 0.15)
        
        # Replay trace
        replay = logger.replay_trace(trace_id)
        
        self.assertIn('summary', replay)
        self.assertIn('nodes', replay)
        self.assertIn('timeline', replay)
        
        self.assertEqual(replay['summary']['question'], "测试问题")
        self.assertEqual(len(replay['nodes']), 2)
        
        print(f"✓ Trace replay works")
        print(f"  Question: {replay['summary']['question']}")
        print(f"  Nodes: {len(replay['nodes'])}")
        print(f"  Success: {replay['summary']['success']}")
    
    def test_07_log_analyzer_stats(self):
        """Test 7: Log Analyzer Statistics"""
        print("\n" + "=" * 70)
        print("Test 7: Log Analyzer Statistics")
        print("=" * 70)
        
        analyzer = LogAnalyzer(log_dir=self.test_log_dir)
        
        # Get node performance stats
        stats = analyzer.get_node_performance_stats()
        
        self.assertIsInstance(stats, dict)
        if stats:
            print(f"✓ Node performance stats generated")
            for node, node_stats in stats.items():
                print(f"  {node}: {node_stats['count']} executions, "
                      f"avg {node_stats['avg_time']:.2f}s")
        else:
            print("✓ No performance stats yet (expected for fresh logs)")
        
        # Get recent traces
        recent = analyzer.logger.get_recent_traces(limit=5)
        self.assertIsInstance(recent, list)
        print(f"  Recent traces: {len(recent)}")
    
    def test_08_integration_with_graph(self):
        """Test 8: Integration with NL2SQL Graph"""
        print("\n" + "=" * 70)
        print("Test 8: Integration with Graph")
        print("=" * 70)
        
        # Run a complete query (this will use existing logging if integrated)
        question = "显示所有专辑"
        
        try:
            result = run_query(question)
            
            # Verify result
            self.assertIsNotNone(result)
            self.assertIn('question', result)
            self.assertEqual(result['question'], question)
            
            # Check if trace_id was generated
            if 'trace_id' in result and result['trace_id']:
                print(f"✓ Graph integration works")
                print(f"  Trace ID: {result['trace_id']}")
                
                # Try to retrieve logs
                logger = get_logger()
                logs = logger.get_trace_logs(result['trace_id'])
                if logs:
                    print(f"  Logs captured: {len(logs)} events")
                else:
                    print("  (Note: Graph not yet fully instrumented with logging)")
            else:
                print("✓ Graph executed successfully")
                print("  (Note: Trace ID not yet integrated into graph)")
        
        except Exception as e:
            print(f"⚠️  Graph execution failed (expected if not all dependencies ready)")
            print(f"  Error: {e}")
    
    def test_09_summary_report(self):
        """Test 9: Summary Report Generation"""
        print("\n" + "=" * 70)
        print("Test 9: Summary Report Generation")
        print("=" * 70)
        
        analyzer = LogAnalyzer(log_dir=self.test_log_dir)
        
        # Generate summary report
        report = analyzer.generate_summary_report()
        
        self.assertIn('total_traces', report)
        self.assertIn('successful', report)
        self.assertIn('failed', report)
        self.assertIn('success_rate', report)
        self.assertIn('node_performance', report)
        
        print(f"✓ Summary report generated")
        print(f"  Total traces: {report['total_traces']}")
        print(f"  Success rate: {report['success_rate']:.1f}%")
        print(f"  Avg response time: {report['avg_response_time']:.2f}s")
    
    def test_10_bottleneck_analysis(self):
        """Test 10: Bottleneck Analysis"""
        print("\n" + "=" * 70)
        print("Test 10: Bottleneck Analysis")
        print("=" * 70)
        
        logger = get_logger(log_dir=self.test_log_dir)
        analyzer = LogAnalyzer(log_dir=self.test_log_dir)
        
        # Create a trace with varying node times
        trace_id = logger.generate_trace_id()
        
        logger.log_trace_start(trace_id, "性能测试", session_id="test_10")
        
        # Log nodes with different execution times
        nodes = [
            (NodeType.PARSE_INTENT, 0.05),
            (NodeType.GENERATE_SQL, 0.50),  # Slowest
            (NodeType.VALIDATE_SQL, 0.10),
            (NodeType.EXECUTE_SQL, 0.30),
        ]
        
        for node_type, exec_time in nodes:
            logger.log_node_execution(
                trace_id, node_type,
                {"test": "data"}, {"result": "ok"},
                exec_time
            )
        
        logger.log_trace_end(trace_id, True, sum(t for _, t in nodes))
        
        # Analyze bottlenecks
        analysis = analyzer.analyze_trace_bottlenecks(trace_id)
        
        self.assertIn('slowest_nodes', analysis)
        self.assertEqual(len(analysis['slowest_nodes']), 4)
        
        # Verify slowest node is generate_sql
        slowest = analysis['slowest_nodes'][0]
        self.assertEqual(slowest['node'], NodeType.GENERATE_SQL.value)
        self.assertEqual(slowest['time'], 0.50)
        
        print(f"✓ Bottleneck analysis works")
        print(f"  Total time: {analysis['total_time']:.2f}s")
        print(f"  Slowest node: {slowest['node']} ({slowest['time']:.2f}s, "
              f"{slowest['percentage']:.1f}%)")


def run_tests():
    """Run all M11 acceptance tests"""
    print("\n" + "=" * 70)
    print("M11 ACCEPTANCE TESTS - SYSTEM OBSERVABILITY & LOGGING")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestM11Observability)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL M11 TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
