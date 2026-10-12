#!/usr/bin/env python3
"""
Analyze 110.dynamic-html benchmark results (AWS vs Azure)
"""

import json
import statistics

def load_results(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_metrics(data):
    """Extract metrics from benchmark results"""
    invocations = list(data['_invocations'].values())[0]

    cold_starts = []
    warm_starts = []

    for inv_id, inv_data in invocations.items():
        is_cold = inv_data['stats']['cold_start']
        client_time = inv_data['times']['client'] / 1000  # Convert to ms

        if is_cold:
            cold_starts.append(client_time)
        else:
            warm_starts.append(client_time)

    return {
        'cold_starts': cold_starts,
        'warm_starts': warm_starts,
        'total_invocations': len(invocations)
    }

def calculate_stats(values):
    """Calculate statistics for a list of values"""
    if not values:
        return None
    return {
        'mean': statistics.mean(values),
        'median': statistics.median(values),
        'stdev': statistics.stdev(values) if len(values) > 1 else 0,
        'min': min(values),
        'max': max(values),
        'count': len(values)
    }

def main():
    # Load results
    aws_data = load_results('110_dynamic_html_aws_20251205.json')
    azure_data = load_results('110_dynamic_html_azure_20251205.json')

    # Extract metrics
    aws_metrics = extract_metrics(aws_data)
    azure_metrics = extract_metrics(azure_data)

    # Calculate statistics
    aws_cold = calculate_stats(aws_metrics['cold_starts'])
    aws_warm = calculate_stats(aws_metrics['warm_starts'])
    azure_cold = calculate_stats(azure_metrics['cold_starts'])
    azure_warm = calculate_stats(azure_metrics['warm_starts'])

    # Print results
    print("=" * 80)
    print("110.dynamic-html Benchmark Results: AWS vs Azure")
    print("=" * 80)
    print()

    print("COLD START PERFORMANCE")
    print("-" * 80)
    if aws_cold and azure_cold:
        print(f"AWS:   {aws_cold['mean']:.2f}ms (n={aws_cold['count']})")
        print(f"Azure: {azure_cold['mean']:.2f}ms (n={azure_cold['count']})")
        speedup = aws_cold['mean'] / azure_cold['mean']
        winner = "Azure" if speedup > 1 else "AWS"
        print(f"Winner: {winner} ({abs(speedup):.2f}x {'faster' if speedup > 1 else 'slower'})")
    print()

    print("WARM START PERFORMANCE")
    print("-" * 80)
    if aws_warm and azure_warm:
        print(f"AWS:   {aws_warm['mean']:.2f}ms ± {aws_warm['stdev']:.2f}ms (n={aws_warm['count']})")
        print(f"Azure: {azure_warm['mean']:.2f}ms ± {azure_warm['stdev']:.2f}ms (n={azure_warm['count']})")
        speedup = aws_warm['mean'] / azure_warm['mean']
        winner = "Azure" if speedup > 1 else "AWS"
        print(f"Winner: {winner} ({abs(speedup):.2f}x {'faster' if speedup > 1 else 'slower'})")
    print()

    print("DETAILED STATISTICS")
    print("-" * 80)
    print("\nAWS Cold Starts:")
    if aws_cold:
        for key, value in aws_cold.items():
            if key != 'count':
                print(f"  {key:10s}: {value:.2f}ms")

    print("\nAWS Warm Starts:")
    if aws_warm:
        for key, value in aws_warm.items():
            if key != 'count':
                print(f"  {key:10s}: {value:.2f}ms")

    print("\nAzure Cold Starts:")
    if azure_cold:
        for key, value in azure_cold.items():
            if key != 'count':
                print(f"  {key:10s}: {value:.2f}ms")

    print("\nAzure Warm Starts:")
    if azure_warm:
        for key, value in azure_warm.items():
            if key != 'count':
                print(f"  {key:10s}: {value:.2f}ms")

    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
