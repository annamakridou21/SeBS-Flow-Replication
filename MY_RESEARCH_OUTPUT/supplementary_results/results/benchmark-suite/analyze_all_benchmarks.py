#!/usr/bin/env python3
"""
Comprehensive analysis of AWS vs Azure benchmarks
Analyzes: 110.dynamic-html, 210.thumbnailer, 311.compression
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

def analyze_benchmark(name, aws_file, azure_file):
    """Analyze a single benchmark"""
    print(f"\n{'='*80}")
    print(f"BENCHMARK: {name}")
    print(f"{'='*80}\n")

    # Load results
    aws_data = load_results(aws_file)
    azure_data = load_results(azure_file)

    # Extract metrics
    aws_metrics = extract_metrics(aws_data)
    azure_metrics = extract_metrics(azure_data)

    # Calculate statistics
    aws_cold = calculate_stats(aws_metrics['cold_starts'])
    aws_warm = calculate_stats(aws_metrics['warm_starts'])
    azure_cold = calculate_stats(azure_metrics['cold_starts'])
    azure_warm = calculate_stats(azure_metrics['warm_starts'])

    # Print cold start comparison
    print("COLD START PERFORMANCE")
    print("-" * 80)
    if aws_cold and azure_cold:
        print(f"AWS:   {aws_cold['mean']:.2f}ms (n={aws_cold['count']})")
        print(f"Azure: {azure_cold['mean']:.2f}ms (n={azure_cold['count']})")
        speedup = aws_cold['mean'] / azure_cold['mean']
        winner = "Azure" if speedup > 1 else "AWS"
        factor = abs(speedup) if speedup > 1 else abs(1/speedup)
        print(f"Winner: {winner} ({factor:.2f}x faster)")
    print()

    # Print warm start comparison
    print("WARM START PERFORMANCE")
    print("-" * 80)
    if aws_warm and azure_warm:
        print(f"AWS:   {aws_warm['mean']:.2f}ms ± {aws_warm['stdev']:.2f}ms (n={aws_warm['count']})")
        print(f"Azure: {azure_warm['mean']:.2f}ms ± {azure_warm['stdev']:.2f}ms (n={azure_warm['count']})")
        speedup = aws_warm['mean'] / azure_warm['mean']
        winner = "Azure" if speedup > 1 else "AWS"
        factor = abs(speedup) if speedup > 1 else abs(1/speedup)
        print(f"Winner: {winner} ({factor:.2f}x faster)")
    print()

    return {
        'name': name,
        'aws_cold': aws_cold,
        'aws_warm': aws_warm,
        'azure_cold': azure_cold,
        'azure_warm': azure_warm
    }

def main():
    print("\n" + "="*80)
    print("AWS vs Azure Serverless Performance Comparison")
    print("Date: December 5, 2025")
    print("="*80)

    benchmarks = [
        {
            'name': '110.dynamic-html (Pure Compute)',
            'aws': '110_dynamic_html_aws_20251205.json',
            'azure': '110_dynamic_html_azure_20251205.json'
        },
        {
            'name': '210.thumbnailer (Image Processing)',
            'aws': '210_thumbnailer_aws_20251205.json',
            'azure': '210_thumbnailer_azure_20251205.json'
        },
        {
            'name': '311.compression (CPU-Intensive)',
            'aws': '311_compression_aws_20251205.json',
            'azure': '311_compression_azure_20251205.json'
        }
    ]

    results = []
    for bench in benchmarks:
        result = analyze_benchmark(bench['name'], bench['aws'], bench['azure'])
        results.append(result)

    # Summary table
    print("\n" + "="*80)
    print("SUMMARY: AWS vs Azure Performance")
    print("="*80)
    print()
    print(f"{'Benchmark':<35} {'Cold Start Winner':<20} {'Warm Start Winner':<20}")
    print("-" * 80)

    for r in results:
        if r['aws_cold'] and r['azure_cold']:
            cold_speedup = r['aws_cold']['mean'] / r['azure_cold']['mean']
            cold_winner = f"Azure ({cold_speedup:.2f}x)" if cold_speedup > 1 else f"AWS ({1/cold_speedup:.2f}x)"
        else:
            cold_winner = "N/A"

        if r['aws_warm'] and r['azure_warm']:
            warm_speedup = r['aws_warm']['mean'] / r['azure_warm']['mean']
            warm_winner = f"Azure ({warm_speedup:.2f}x)" if warm_speedup > 1 else f"AWS ({1/warm_speedup:.2f}x)"
        else:
            warm_winner = "N/A"

        print(f"{r['name']:<35} {cold_winner:<20} {warm_winner:<20}")

    print("\n" + "="*80)

if __name__ == '__main__':
    main()
