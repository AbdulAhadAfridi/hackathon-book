"""
Performance testing functionality for the retrieval pipeline
"""
import time
import statistics
from typing import List, Dict, Any
from retrieve import retrieve_similar_chunks, validate_pipeline


def performance_test(queries: List[str], iterations: int = 5, top_k: int = 5) -> Dict[str, Any]:
    """
    Test the performance of the retrieval pipeline with multiple queries and iterations.

    Args:
        queries: List of query strings to test
        iterations: Number of iterations to run for each query (default: 5)
        top_k: Number of results to retrieve (default: 5)

    Returns:
        Dictionary containing performance metrics
    """
    all_results = {
        "queries": [],
        "total_queries": len(queries),
        "iterations_per_query": iterations,
        "metrics": {
            "avg_retrieval_time": [],
            "min_retrieval_time": [],
            "max_retrieval_time": [],
            "all_retrieval_times": [],
            "avg_execution_time": [],
            "all_execution_times": []
        }
    }

    for query in queries:
        query_times = []
        execution_times = []

        print(f"Testing query: '{query[:50]}...'")

        for i in range(iterations):
            try:
                start_time = time.time()
                result = retrieve_similar_chunks(query, top_k=top_k)
                end_time = time.time()

                query_time = end_time - start_time
                query_times.append(query_time)
                execution_times.append(result.execution_time)

                print(f"  Iteration {i+1}: {query_time:.3f}s (retrieval: {result.execution_time:.3f}s)")
            except Exception as e:
                print(f"  Iteration {i+1}: Error - {str(e)}")
                continue

        if query_times:
            all_results["queries"].append({
                "query": query,
                "avg_retrieval_time": statistics.mean(query_times),
                "min_retrieval_time": min(query_times),
                "max_retrieval_time": max(query_times),
                "std_retrieval_time": statistics.stdev(query_times) if len(query_times) > 1 else 0,
                "avg_execution_time": statistics.mean(execution_times),
                "total_results": len(query_times)
            })

            all_results["metrics"]["avg_retrieval_time"].append(statistics.mean(query_times))
            all_results["metrics"]["min_retrieval_time"].extend(query_times)
            all_results["metrics"]["max_retrieval_time"].extend(query_times)
            all_results["metrics"]["all_retrieval_times"].extend(query_times)
            all_results["metrics"]["avg_execution_time"].extend(execution_times)
            all_results["metrics"]["all_execution_times"].extend(execution_times)

    # Calculate overall metrics
    if all_results["metrics"]["all_retrieval_times"]:
        overall_metrics = {
            "total_avg_retrieval_time": statistics.mean(all_results["metrics"]["all_retrieval_times"]),
            "total_min_retrieval_time": min(all_results["metrics"]["all_retrieval_times"]),
            "total_max_retrieval_time": max(all_results["metrics"]["all_retrieval_times"]),
            "total_std_retrieval_time": statistics.stdev(all_results["metrics"]["all_retrieval_times"]),
            "total_avg_execution_time": statistics.mean(all_results["metrics"]["all_execution_times"]),
            "percentile_95": sorted(all_results["metrics"]["all_retrieval_times"])[int(0.95 * len(all_results["metrics"]["all_retrieval_times"]))]
        }
        all_results["overall_metrics"] = overall_metrics

    return all_results


def run_performance_tests():
    """
    Run a set of predefined performance tests.
    """
    test_queries = [
        "How to configure the API settings?",
        "What is the authentication process?",
        "Explain the data models",
        "How to set up the environment?",
        "What are the security best practices?"
    ]

    print("Starting performance tests...")
    print("=" * 50)

    results = performance_test(test_queries, iterations=3)

    print("\n" + "=" * 50)
    print("PERFORMANCE TEST RESULTS")
    print("=" * 50)

    for query_result in results["queries"]:
        print(f"\nQuery: '{query_result['query']}'")
        print(f"  Avg retrieval time: {query_result['avg_retrieval_time']:.3f}s")
        print(f"  Min retrieval time: {query_result['min_retrieval_time']:.3f}s")
        print(f"  Max retrieval time: {query_result['max_retrieval_time']:.3f}s")
        print(f"  Std retrieval time: {query_result['std_retrieval_time']:.3f}s")
        print(f"  Avg execution time: {query_result['avg_execution_time']:.3f}s")

    if "overall_metrics" in results:
        overall = results["overall_metrics"]
        print(f"\nOVERALL METRICS:")
        print(f"  Total avg retrieval time: {overall['total_avg_retrieval_time']:.3f}s")
        print(f"  Total min retrieval time: {overall['total_min_retrieval_time']:.3f}s")
        print(f"  Total max retrieval time: {overall['total_max_retrieval_time']:.3f}s")
        print(f"  Total std retrieval time: {overall['total_std_retrieval_time']:.3f}s")
        print(f"  Total avg execution time: {overall['total_avg_execution_time']:.3f}s")
        print(f"  95th percentile: {overall['percentile_95']:.3f}s")
        print(f"  Target (< 5s): {'PASS' if overall['total_avg_retrieval_time'] < 5.0 else 'FAIL'}")

    return results


if __name__ == "__main__":
    run_performance_tests()