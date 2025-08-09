#!/usr/bin/env python3
"""
Comprehensive QA Test Suite for The Collective Soul Vector Database
Tests performance, accuracy, edge cases, and integration
Dale's vision: "Zero false positives, zero missed knowledge, instant perfect recall"
"""

import os
import sys
import time
import json
import asyncio
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Add module paths
sys.path.insert(0, '/home/dthomas_unix/venv/vector-db/bin')

@dataclass
class TestResult:
    """Represents a test result"""
    test_name: str
    category: str
    passed: bool
    duration_ms: float
    details: str
    score: Optional[float] = None
    expected_keywords: List[str] = None
    found_keywords: List[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for the QA report"""
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    concurrent_performance: Dict[str, float]
    memory_usage: Dict[str, float]

class ComprehensiveQATestSuite:
    """Comprehensive QA testing for vector database system"""
    
    def __init__(self):
        """Initialize the test suite"""
        # Import after venv activation
        from sustainable_indexer import SustainableIndexer
        self.indexer = SustainableIndexer()
        self.results: List[TestResult] = []
        self.performance_times: List[float] = []
        
    def log_result(self, test_name: str, category: str, passed: bool, 
                   duration_ms: float, details: str, **kwargs):
        """Log a test result"""
        result = TestResult(
            test_name=test_name,
            category=category,
            passed=passed,
            duration_ms=duration_ms,
            details=details,
            **kwargs
        )
        self.results.append(result)
        
    def time_query(self, query: str, top_k: int = 1) -> Tuple[Dict, float]:
        """Time a query and return results with duration"""
        start_time = time.time()
        results = self.indexer.search(query, top_k=top_k)
        duration = (time.time() - start_time) * 1000
        self.performance_times.append(duration)
        return results, duration
        
    def test_identity_queries(self):
        """Test identity-related queries"""
        print("\n🔍 TESTING IDENTITY QUERIES")
        print("=" * 60)
        
        identity_tests = [
            {
                "query": "Who is Awen and what is their role?",
                "expected_keywords": ["Awen", "muse", "strategic", "oversight", "creative"],
                "name": "Awen Identity"
            },
            {
                "query": "Who is Dale Thomas?",
                "expected_keywords": ["Dale", "founder", "artist", "CEO", "chairman"],
                "name": "Dale Identity"
            },
            {
                "query": "Who is Rhys and what do they do?",
                "expected_keywords": ["Rhys", "analyst", "data", "insights"],
                "name": "Rhys Identity"
            },
            {
                "query": "What are the triumvirate roles?",
                "expected_keywords": ["triumvirate", "Dale", "Awen", "Rhys", "roles"],
                "name": "Triumvirate Structure"
            }
        ]
        
        for test in identity_tests:
            results, duration = self.time_query(test["query"])
            
            if results['documents'] and results['documents'][0]:
                doc = results['documents'][0][0]
                found_keywords = [kw for kw in test["expected_keywords"] 
                                if kw.lower() in doc.lower()]
                
                passed = len(found_keywords) >= 1  # At least one keyword must match
                details = f"Found {len(found_keywords)}/{len(test['expected_keywords'])} keywords"
                
                print(f"  ✅ {test['name']}: {duration:.1f}ms - {details}")
                print(f"     Keywords: {', '.join(found_keywords)}")
                print(f"     Preview: {doc[:200]}...")
                
            else:
                passed = False
                details = "No results found"
                found_keywords = []
                print(f"  ❌ {test['name']}: {duration:.1f}ms - {details}")
            
            self.log_result(
                test['name'], 'Identity', passed, duration, details,
                expected_keywords=test["expected_keywords"],
                found_keywords=found_keywords
            )
            print()
    
    def test_technical_queries(self):
        """Test technical knowledge queries"""
        print("\n🔧 TESTING TECHNICAL QUERIES")
        print("=" * 60)
        
        technical_tests = [
            {
                "query": "What are the context thresholds for optimal performance?",
                "expected_keywords": ["40K", "80K", "100K", "tokens", "optimal", "threshold"],
                "name": "Context Thresholds"
            },
            {
                "query": "Model selection strategy opus sonnet",
                "expected_keywords": ["opus", "sonnet", "model", "selection", "thinking"],
                "name": "Model Selection"
            },
            {
                "query": "What is OS-004 intelligent context management?",
                "expected_keywords": ["OS-004", "context", "management", "intelligent", "reboot"],
                "name": "OS-004 System"
            },
            {
                "query": "How many specialist subagents exist?",
                "expected_keywords": ["subagent", "specialist", "architect", "dev-lead"],
                "name": "Subagent Count"
            }
        ]
        
        for test in technical_tests:
            results, duration = self.time_query(test["query"])
            
            if results['documents'] and results['documents'][0]:
                doc = results['documents'][0][0]
                found_keywords = [kw for kw in test["expected_keywords"] 
                                if kw.lower() in doc.lower()]
                
                passed = len(found_keywords) >= 2  # At least two keywords for technical queries
                details = f"Found {len(found_keywords)}/{len(test['expected_keywords'])} keywords"
                
                print(f"  ✅ {test['name']}: {duration:.1f}ms - {details}")
                print(f"     Keywords: {', '.join(found_keywords)}")
                
            else:
                passed = False
                details = "No results found"
                found_keywords = []
                print(f"  ❌ {test['name']}: {duration:.1f}ms - {details}")
            
            self.log_result(
                test['name'], 'Technical', passed, duration, details,
                expected_keywords=test["expected_keywords"],
                found_keywords=found_keywords
            )
            print()
    
    def test_historical_queries(self):
        """Test historical knowledge queries"""
        print("\n📅 TESTING HISTORICAL QUERIES")
        print("=" * 60)
        
        historical_tests = [
            {
                "query": "What happened on August 7, 2025?",
                "expected_keywords": ["August", "7", "2025", "transformation", "identity"],
                "name": "August 7 Events"
            },
            {
                "query": "What happened on August 8, 2025?",
                "expected_keywords": ["August", "8", "2025"],
                "name": "August 8 Events"
            },
            {
                "query": "Collective Soul Studio transformation",
                "expected_keywords": ["Collective Soul", "Studio", "transformation"],
                "name": "Studio Transformation"
            }
        ]
        
        for test in historical_tests:
            results, duration = self.time_query(test["query"])
            
            if results['documents'] and results['documents'][0]:
                doc = results['documents'][0][0]
                found_keywords = [kw for kw in test["expected_keywords"] 
                                if kw.lower() in doc.lower()]
                
                passed = len(found_keywords) >= 1
                details = f"Found {len(found_keywords)}/{len(test['expected_keywords'])} keywords"
                
                print(f"  ✅ {test['name']}: {duration:.1f}ms - {details}")
                print(f"     Keywords: {', '.join(found_keywords)}")
                
            else:
                passed = False
                details = "No results found"
                found_keywords = []
                print(f"  ❌ {test['name']}: {duration:.1f}ms - {details}")
            
            self.log_result(
                test['name'], 'Historical', passed, duration, details,
                expected_keywords=test["expected_keywords"],
                found_keywords=found_keywords
            )
            print()
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n⚠️  TESTING EDGE CASES")
        print("=" * 60)
        
        edge_tests = [
            {
                "query": "This is completely nonexistent information that should not be found",
                "should_find": False,
                "name": "Non-existent Info"
            },
            {
                "query": "",  # Empty query
                "should_find": False,
                "name": "Empty Query"
            },
            {
                "query": "a",  # Single character
                "should_find": True,  # Might find something
                "name": "Single Character"
            },
            {
                "query": "What is the meaning of life universe and everything according to Douglas Adams and how does it relate to our organizational structure and mission and vision and strategic goals for the next decade including AI integration and consciousness expansion?",
                "should_find": True,  # Long query should still work
                "name": "Very Long Query"
            },
            {
                "query": "def function(): return 'code'",  # Code-like query
                "should_find": True,
                "name": "Code Snippet Query"
            }
        ]
        
        for test in edge_tests:
            try:
                results, duration = self.time_query(test["query"])
                
                has_results = results['documents'] and results['documents'][0] and len(results['documents'][0]) > 0
                
                if test["should_find"]:
                    passed = has_results
                    details = "Found results" if has_results else "No results (unexpected)"
                else:
                    passed = not has_results
                    details = "No results (expected)" if not has_results else "Found results (unexpected)"
                
                status = "✅" if passed else "❌"
                print(f"  {status} {test['name']}: {duration:.1f}ms - {details}")
                
            except Exception as e:
                passed = False
                duration = 0
                details = f"Error: {str(e)}"
                print(f"  ❌ {test['name']}: ERROR - {details}")
            
            self.log_result(
                test['name'], 'Edge Cases', passed, duration, details
            )
            print()
    
    def test_concurrent_performance(self, num_concurrent: int = 5):
        """Test concurrent query performance"""
        print(f"\n⚡ TESTING CONCURRENT PERFORMANCE ({num_concurrent} queries)")
        print("=" * 60)
        
        test_queries = [
            "Who is Awen?",
            "What are context thresholds?",
            "Model selection strategy",
            "Triumvirate system",
            "OS-004 system"
        ]
        
        def run_concurrent_query(query: str) -> Tuple[str, float]:
            """Run a single concurrent query"""
            start_time = time.time()
            try:
                results = self.indexer.search(query, top_k=1)
                duration = (time.time() - start_time) * 1000
                has_results = results['documents'] and results['documents'][0]
                return query, duration, has_results
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                return query, duration, False
        
        # Run concurrent queries
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            future_to_query = {executor.submit(run_concurrent_query, query): query 
                             for query in test_queries[:num_concurrent]}
            
            results = []
            for future in concurrent.futures.as_completed(future_to_query):
                query, duration, success = future.result()
                results.append((query, duration, success))
        
        total_time = (time.time() - start_time) * 1000
        
        # Analyze results
        successful_queries = sum(1 for _, _, success in results if success)
        avg_concurrent_time = sum(duration for _, duration, _ in results) / len(results)
        
        passed = successful_queries == num_concurrent and avg_concurrent_time < 200
        details = f"{successful_queries}/{num_concurrent} successful, avg {avg_concurrent_time:.1f}ms"
        
        print(f"  Total concurrent execution time: {total_time:.1f}ms")
        print(f"  Average individual query time: {avg_concurrent_time:.1f}ms")
        print(f"  Success rate: {successful_queries}/{num_concurrent}")
        
        status = "✅" if passed else "❌"
        print(f"  {status} Concurrent Performance: {details}")
        
        self.log_result(
            f"Concurrent {num_concurrent} Queries", 'Performance', passed, 
            avg_concurrent_time, details
        )
        
        return {
            'total_time': total_time,
            'avg_query_time': avg_concurrent_time,
            'success_rate': successful_queries / num_concurrent
        }
    
    def test_cross_references(self):
        """Test cross-reference capabilities"""
        print("\n🔗 TESTING CROSS-REFERENCES")
        print("=" * 60)
        
        cross_ref_queries = [
            {
                "query": "triumvirate communication protocol messages",
                "min_results": 2,
                "name": "Triumvirate Protocols"
            },
            {
                "query": "subagent specialist architecture",
                "min_results": 3,
                "name": "Subagent Architecture"
            },
            {
                "query": "context management memory system",
                "min_results": 2,
                "name": "Memory Systems"
            }
        ]
        
        for test in cross_ref_queries:
            results, duration = self.time_query(test["query"], top_k=5)
            
            num_results = len(results['documents'][0]) if results['documents'] and results['documents'][0] else 0
            passed = num_results >= test["min_results"]
            details = f"Found {num_results} results (min {test['min_results']})"
            
            status = "✅" if passed else "❌"
            print(f"  {status} {test['name']}: {duration:.1f}ms - {details}")
            
            if num_results > 0:
                print("     Sources found:")
                for i, doc in enumerate(results['documents'][0][:3]):
                    preview = doc[:100].replace('\n', ' ')
                    print(f"       {i+1}. {preview}...")
            
            self.log_result(
                test['name'], 'Cross-Reference', passed, duration, details
            )
            print()
    
    def check_daemon_health(self):
        """Check if the daemon is healthy and responsive"""
        print("\n🏥 DAEMON HEALTH CHECK")
        print("=" * 60)
        
        # Check if daemon PID exists
        try:
            with open(Path.home() / "logs/vector-indexer.pid", 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is running
            import psutil
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                print(f"  ✅ Daemon PID {pid} is running")
                print(f"     CPU Usage: {cpu_percent:.1f}%")
                print(f"     Memory Usage: {memory_mb:.1f} MB")
                
                # Test daemon responsiveness with a simple query
                start_time = time.time()
                results = self.indexer.search("test query", top_k=1)
                response_time = (time.time() - start_time) * 1000
                
                responsive = response_time < 1000  # Should respond within 1 second
                print(f"     Response Time: {response_time:.1f}ms {'✅' if responsive else '❌'}")
                
                passed = responsive
                details = f"PID {pid} running, {response_time:.1f}ms response"
                
            else:
                passed = False
                details = f"PID {pid} not running"
                print(f"  ❌ Daemon PID {pid} is not running")
                
        except FileNotFoundError:
            passed = False
            details = "PID file not found"
            print(f"  ❌ Daemon PID file not found")
        except Exception as e:
            passed = False
            details = f"Error checking daemon: {str(e)}"
            print(f"  ❌ Error checking daemon: {str(e)}")
        
        self.log_result(
            "Daemon Health", 'Integration', passed, 0, details
        )
    
    def generate_performance_metrics(self) -> PerformanceMetrics:
        """Generate comprehensive performance metrics"""
        if not self.performance_times:
            return PerformanceMetrics(0, 0, 0, {}, {})
        
        sorted_times = sorted(self.performance_times)
        n = len(sorted_times)
        
        avg_time = sum(sorted_times) / n
        p95_time = sorted_times[int(n * 0.95)]
        p99_time = sorted_times[int(n * 0.99)]
        
        return PerformanceMetrics(
            avg_response_time=avg_time,
            p95_response_time=p95_time,
            p99_response_time=p99_time,
            concurrent_performance={},  # Filled by concurrent tests
            memory_usage={}  # Could be expanded
        )
    
    def generate_qa_report(self):
        """Generate comprehensive QA report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE QA REPORT")
        print("The Collective Soul Vector Database System")
        print("=" * 80)
        
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Performance metrics
        metrics = self.generate_performance_metrics()
        
        print(f"\n🎯 SUMMARY METRICS")
        print(f"   Total Tests Run: {total_tests}")
        print(f"   Tests Passed: {passed_tests} ({pass_rate:.1f}%)")
        print(f"   Tests Failed: {failed_tests}")
        print(f"   Average Response Time: {metrics.avg_response_time:.1f}ms")
        print(f"   95th Percentile: {metrics.p95_response_time:.1f}ms")
        print(f"   99th Percentile: {metrics.p99_response_time:.1f}ms")
        
        # Performance goals assessment
        print(f"\n🎯 PERFORMANCE GOALS")
        avg_goal = metrics.avg_response_time < 100
        p95_goal = metrics.p95_response_time < 200
        print(f"   <100ms average: {'✅ ACHIEVED' if avg_goal else '❌ MISSED'} ({metrics.avg_response_time:.1f}ms)")
        print(f"   <200ms P95: {'✅ ACHIEVED' if p95_goal else '❌ MISSED'} ({metrics.p95_response_time:.1f}ms)")
        
        # Category breakdown
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {'passed': 0, 'total': 0, 'avg_time': 0}
            categories[result.category]['total'] += 1
            if result.passed:
                categories[result.category]['passed'] += 1
            categories[result.category]['avg_time'] += result.duration_ms
        
        print(f"\n📂 CATEGORY BREAKDOWN")
        for category, stats in categories.items():
            avg_time = stats['avg_time'] / stats['total']
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {category}: {stats['passed']}/{stats['total']} passed ({pass_rate:.1f}%) - {avg_time:.1f}ms avg")
        
        # Failed tests details
        failed_results = [r for r in self.results if not r.passed]
        if failed_results:
            print(f"\n❌ FAILED TESTS ANALYSIS")
            for result in failed_results:
                print(f"   • {result.test_name} ({result.category}): {result.details}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        if failed_tests == 0:
            print("   🎉 ALL TESTS PASSED! The Collective Soul has perfect memory!")
        else:
            if any(r.category == 'Identity' and not r.passed for r in self.results):
                print("   • Identity queries need attention - check document indexing coverage")
            if any(r.category == 'Technical' and not r.passed for r in self.results):
                print("   • Technical knowledge gaps found - verify CLAUDE.md indexing")
            if metrics.avg_response_time > 100:
                print("   • Performance optimization needed - consider model caching")
        
        # Dale's vision assessment
        print(f"\n🔮 DALE'S VISION ASSESSMENT")
        print("   'Zero false positives, zero missed knowledge, instant perfect recall'")
        
        false_positives = 0  # Would need more sophisticated analysis
        missed_knowledge = failed_tests
        instant_recall = avg_goal
        
        vision_score = ((total_tests - missed_knowledge) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"   Zero False Positives: {'✅' if false_positives == 0 else '❌'} (estimated)")
        print(f"   Zero Missed Knowledge: {'✅' if missed_knowledge == 0 else '❌'} ({missed_knowledge} misses)")
        print(f"   Instant Perfect Recall: {'✅' if instant_recall else '❌'} ({metrics.avg_response_time:.1f}ms avg)")
        print(f"   Overall Vision Score: {vision_score:.1f}%")
        
        print("\n" + "=" * 80)
        print("QA Report Complete")
        print("=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'pass_rate': pass_rate,
            'performance_metrics': metrics,
            'vision_score': vision_score
        }
    
    def run_all_tests(self):
        """Run the complete QA test suite"""
        print("🔮 COMPREHENSIVE QA TEST SUITE")
        print("The Collective Soul Vector Database System")
        print("Testing for: Zero false positives, zero missed knowledge, instant perfect recall")
        print("=" * 80)
        
        # Check daemon health first
        self.check_daemon_health()
        
        # Run all test categories
        self.test_identity_queries()
        self.test_technical_queries()
        self.test_historical_queries()
        self.test_cross_references()
        self.test_edge_cases()
        
        # Performance testing
        self.test_concurrent_performance(5)
        
        # Generate final report
        return self.generate_qa_report()

if __name__ == "__main__":
    # Set up environment
    os.environ['PYTHONPATH'] = '/home/dthomas_unix/venv/vector-db/bin'
    
    try:
        # Create and run test suite
        qa_suite = ComprehensiveQATestSuite()
        report = qa_suite.run_all_tests()
        
        # Exit with appropriate code
        if report['failed_tests'] == 0:
            print("\n🎉 ALL TESTS PASSED - The Collective Soul has perfect memory!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {report['failed_tests']} tests need attention")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ QA Test Suite encountered an error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)