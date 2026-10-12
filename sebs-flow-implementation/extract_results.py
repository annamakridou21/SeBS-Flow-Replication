#!/usr/bin/env python3
"""
Extract SeBS-Flow results for AWS vs Azure comparison analysis
Usage: python3 extract_results.py experiments.json
"""

import json
import sys
import csv
from datetime import datetime

def extract_function_metrics(invocations, function_name):
    """Extract key performance metrics for a function"""
    if function_name not in invocations:
        return []
    
    results = []
    for request_id, data in invocations[function_name].items():
        result = {
            'request_id': request_id,
            'function_name': function_name,
            'cold_start': data['stats']['cold_start'],
            'execution_time_ms': data['times']['benchmark'] / 1000,  # Convert to ms
            'total_time_ms': data['times']['client'] / 1000,
            'billed_time_ms': data['billing']['_billed_time'],
            'memory_allocated_mb': data['billing']['_memory'],
            'memory_used_mb': data['stats']['memory_used'],
            'initialization_time_ms': data['provider_times']['initialization'] / 1000,
            'failure': data['stats']['failure'],
            'timestamp': data['times']['client_begin']
        }
        
        # Add benchmark-specific metrics if available
        if 'result' in data['output'] and 'measurement' in data['output']['result']:
            measurement = data['output']['result']['measurement']
            result.update({
                'upload_time_ms': measurement.get('upload_time', 0) / 1000,
                'upload_size_bytes': measurement.get('upload_size', 0),
                'download_time_ms': measurement.get('download_time', 0) / 1000,
                'download_size_bytes': measurement.get('download_size', 0),
                'compute_time_ms': measurement.get('compute_time', 0) / 1000
            })
        
        results.append(result)
    
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 extract_results.py experiments.json")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    invocations = data.get('_invocations', {})
    
    # Extract results for all functions
    all_results = []
    for function_name in invocations.keys():
        results = extract_function_metrics(invocations, function_name)
        all_results.extend(results)
    
    if not all_results:
        print("No function results found in the data")
        return
    
    # Write CSV output
    output_file = f"aws_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [
            'function_name', 'request_id', 'timestamp', 'cold_start',
            'execution_time_ms', 'total_time_ms', 'billed_time_ms',
            'memory_allocated_mb', 'memory_used_mb', 'initialization_time_ms',
            'upload_time_ms', 'upload_size_bytes', 'download_time_ms', 
            'download_size_bytes', 'compute_time_ms', 'failure'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in all_results:
            writer.writerow(result)
    
    print(f"Results exported to: {output_file}")
    
    # Print summary statistics
    print(f"\nSummary for {len(all_results)} invocations:")
    
    cold_starts = [r for r in all_results if r['cold_start']]
    warm_starts = [r for r in all_results if not r['cold_start']]
    
    if cold_starts:
        avg_cold = sum(r['execution_time_ms'] for r in cold_starts) / len(cold_starts)
        print(f"Cold starts: {len(cold_starts)}, Avg execution time: {avg_cold:.2f}ms")
    
    if warm_starts:
        avg_warm = sum(r['execution_time_ms'] for r in warm_starts) / len(warm_starts)
        print(f"Warm starts: {len(warm_starts)}, Avg execution time: {avg_warm:.2f}ms")
    
    functions = set(r['function_name'] for r in all_results)
    for func in functions:
        func_results = [r for r in all_results if r['function_name'] == func]
        print(f"Function {func}: {len(func_results)} invocations")

if __name__ == "__main__":
    main()