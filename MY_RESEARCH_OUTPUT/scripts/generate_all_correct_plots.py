#!/usr/bin/env python3
"""
Generate ALL corrected plots with proper labels and correct data values
Creates both microbenchmark and workflow plots
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from pathlib import Path

# Set publication style
sb.set_theme()
sb.set_context("paper", font_scale=1.3)
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12

# Colors
colors = sb.color_palette("colorblind")
color_map = {
    "AWS": colors[0],      # Blue
    "Azure": colors[1],    # Orange
}

def load_json(filepath):
    """Load JSON result file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def extract_workflow_times(data, workflow_id):
    """Extract times from workflow results with correct field selection

    CRITICAL: Always use 'client' time for workflows!
    - AWS workflows: client time represents end-to-end orchestration
    - Azure workflows: client time represents end-to-end orchestration
    - The 'benchmark' field in Azure workflows is NOT the orchestration time
    """
    if not data or '_invocations' not in data:
        return None

    cold_times = []
    warm_times = []
    all_times = []

    workflow_key = list(data['_invocations'].keys())[0]
    invocations = data['_invocations'][workflow_key]

    for req_id, invocation in invocations.items():
        if 'times' in invocation and 'client' in invocation['times']:
            # ALWAYS use client time for workflows (both AWS and Azure)
            # This represents the actual end-to-end workflow orchestration time
            time_ms = invocation['times']['client'] / 1000.0

            is_cold = invocation.get('stats', {}).get('cold_start', False)

            all_times.append(time_ms)
            if is_cold:
                cold_times.append(time_ms)
            else:
                warm_times.append(time_ms)

    return {
        'cold': cold_times,
        'warm': warm_times,
        'all': all_times,
        'avg_cold': np.mean(cold_times) if cold_times else 0,
        'avg_warm': np.mean(warm_times) if warm_times else 0,
        'avg_all': np.mean(all_times) if all_times else 0
    }

def plot_workflow_comparison():
    """Create workflow performance comparison plot"""

    workflows = [
        ('620', 'Func-Invo'),
        ('630', 'Parallel-Sleep'),
        ('660', 'Map-Reduce')
    ]

    print("\n=== Loading Workflow Data ===")
    data = {}

    for wf_id, wf_name in workflows:
        aws_file = f'../aws_results/experiments_{wf_id}_aws.json'
        azure_file = f'../azure_results/experiments_{wf_id}.json'

        aws_data = load_json(aws_file)
        azure_data = load_json(azure_file)

        aws_times = extract_workflow_times(aws_data, wf_id)
        azure_times = extract_workflow_times(azure_data, wf_id)

        data[wf_id] = {
            'name': wf_name,
            'AWS': aws_times,
            'Azure': azure_times
        }

        print(f"\n{wf_id} {wf_name}:")
        if aws_times:
            print(f"  AWS: {aws_times['avg_all']:.1f}ms (cold: {aws_times['avg_cold']:.1f}ms, warm: {aws_times['avg_warm']:.1f}ms)")
        if azure_times:
            print(f"  Azure: {azure_times['avg_all']:.1f}ms (cold: {azure_times['avg_cold']:.1f}ms, warm: {azure_times['avg_warm']:.1f}ms)")

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    x_labels = [data[wf_id]['name'] for wf_id, _ in workflows]
    x = np.arange(len(workflows))
    width = 0.35

    # Collect data
    aws_latencies = []
    azure_latencies = []

    for wf_id, _ in workflows:
        aws_lat = data[wf_id]['AWS']['avg_all'] if data[wf_id]['AWS'] else 0
        azure_lat = data[wf_id]['Azure']['avg_all'] if data[wf_id]['Azure'] else 0
        aws_latencies.append(aws_lat)
        azure_latencies.append(azure_lat)

    # Plot bars
    bars1 = ax.bar(x - width/2, aws_latencies, width, label='AWS Lambda',
                   color=color_map['AWS'], edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + width/2, azure_latencies, width, label='Azure Functions',
                   color=color_map['Azure'], edgecolor='black', linewidth=1.2)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Formatting
    ax.set_xlabel('Workflow Benchmark', fontsize=14, fontweight='bold')
    ax.set_ylabel('Latency (ms)', fontsize=14, fontweight='bold')
    ax.set_title('Workflow Performance', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=12)
    ax.legend(loc='upper left', fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    output_file = '../plots/workflow_performance_correct.pdf'
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f"\n Saved: {output_file}")
    plt.close()

def extract_function_times(data):
    """Extract function benchmark times"""
    if not data or '_invocations' not in data:
        return None

    cold_times = []
    warm_times = []

    # Get all invocations
    for benchmark_key in data['_invocations']:
        invocations = data['_invocations'][benchmark_key]
        for req_id, invocation in invocations.items():
            if 'times' in invocation:
                # Use benchmark time if available, otherwise client
                time_ms = invocation['times'].get('benchmark', invocation['times'].get('client', 0)) / 1000.0
                is_cold = invocation.get('stats', {}).get('cold_start', False)

                if is_cold:
                    cold_times.append(time_ms)
                else:
                    warm_times.append(time_ms)

    return {
        'cold': cold_times,
        'warm': warm_times,
        'avg_cold': np.mean(cold_times) if cold_times else 0,
        'avg_warm': np.mean(warm_times) if warm_times else 0
    }

def plot_microbenchmark_comparison():
    """Create microbenchmark performance comparison plot"""

    benchmarks = [
        ('110', '110\nHTML'),
        ('210', '210\nImage'),
        ('311', '311\nCompress'),
        ('050', '050\nMatrix')
    ]

    print("\n=== Loading Microbenchmark Data ===")
    data = {}

    for bench_id, bench_label in benchmarks:
        # Map benchmark IDs to actual file patterns
        bench_names = {
            '110': 'dynamic_html',
            '210': 'thumbnailer',
            '311': 'compression',
            '050': 'matrix_multiply'
        }
        name = bench_names.get(bench_id, '')

        # Try both date formats (20251205 for 110/210/311, 20251218 for 050)
        aws_file = f'../aws_results/{bench_id}_{name}_aws_20251205.json'
        if not Path(aws_file).exists():
            aws_file = f'../aws_results/{bench_id}_{name}_aws_20251218.json'

        azure_file = f'../azure_results/{bench_id}_{name}_azure_20251205.json'
        if not Path(azure_file).exists():
            azure_file = f'../azure_results/{bench_id}_{name}_azure_20251218.json'

        aws_data = load_json(aws_file)
        azure_data = load_json(azure_file)

        aws_times = extract_function_times(aws_data) if aws_data else None
        azure_times = extract_function_times(azure_data) if azure_data else None

        data[bench_id] = {
            'label': bench_label,
            'AWS': aws_times,
            'Azure': azure_times
        }

        print(f"\n{bench_id}:")
        if aws_times:
            print(f"  AWS - Cold: {aws_times['avg_cold']:.1f}ms, Warm: {aws_times['avg_warm']:.1f}ms")
        if azure_times:
            print(f"  Azure - Cold: {azure_times['avg_cold']:.1f}ms, Warm: {azure_times['avg_warm']:.1f}ms")

    # Create figure with log scale
    fig, ax = plt.subplots(figsize=(10, 6))

    x_labels = [data[bench_id]['label'] for bench_id, _ in benchmarks]
    x = np.arange(len(benchmarks))
    width = 0.2

    # Collect data
    aws_cold = []
    aws_warm = []
    azure_cold = []
    azure_warm = []

    for bench_id, _ in benchmarks:
        if data[bench_id]['AWS']:
            aws_cold.append(data[bench_id]['AWS']['avg_cold'])
            aws_warm.append(data[bench_id]['AWS']['avg_warm'])
        else:
            aws_cold.append(0)
            aws_warm.append(0)

        if data[bench_id]['Azure']:
            azure_cold.append(data[bench_id]['Azure']['avg_cold'])
            azure_warm.append(data[bench_id]['Azure']['avg_warm'])
        else:
            azure_cold.append(0)
            azure_warm.append(0)

    # Plot bars
    ax.bar(x - 1.5*width, aws_cold, width, label='AWS Cold',
           color=color_map['AWS'], edgecolor='black', linewidth=1)
    ax.bar(x - 0.5*width, azure_cold, width, label='Azure Cold',
           color=color_map['Azure'], edgecolor='black', linewidth=1)
    ax.bar(x + 0.5*width, aws_warm, width, label='AWS Warm',
           color=color_map['AWS'], alpha=0.5, hatch='///', edgecolor='black', linewidth=1)
    ax.bar(x + 1.5*width, azure_warm, width, label='Azure Warm',
           color=color_map['Azure'], alpha=0.5, hatch='///', edgecolor='black', linewidth=1)

    # Log scale
    ax.set_yscale('log')

    # Formatting
    ax.set_xlabel('Microbenchmark', fontsize=14, fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontsize=14, fontweight='bold')
    ax.set_title('Microbenchmark Performance', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=12)
    ax.legend(loc='upper left', fontsize=10, ncol=2)
    ax.grid(axis='y', alpha=0.3, linestyle='--', which='both')

    plt.tight_layout()
    output_file = '../plots/microbenchmark_performance_correct.pdf'
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f"\n Saved: {output_file}")
    plt.close()

def plot_combined_overview():
    """Create combined overview plot (side-by-side microbenchmark + workflow)"""

    print("\n=== Creating Combined Overview ===")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # --- Microbenchmarks (Left) ---
    benchmarks = [('110', '110\nHTML'), ('210', '210\nImage'), ('311', '311\nCompress')]

    data_micro = {}
    for bench_id, bench_label in benchmarks:
        bench_names = {'110': 'dynamic_html', '210': 'thumbnailer', '311': 'compression'}
        name = bench_names.get(bench_id, '')

        aws_data = load_json(f'../aws_results/{bench_id}_{name}_aws_20251205.json')
        azure_data = load_json(f'../azure_results/{bench_id}_{name}_azure_20251205.json')

        data_micro[bench_id] = {
            'label': bench_label,
            'AWS': extract_function_times(aws_data) if aws_data else None,
            'Azure': extract_function_times(azure_data) if azure_data else None
        }

    x = np.arange(len(benchmarks))
    width = 0.2

    aws_cold = [data_micro[b]['AWS']['avg_cold'] if data_micro[b]['AWS'] else 0 for b, _ in benchmarks]
    aws_warm = [data_micro[b]['AWS']['avg_warm'] if data_micro[b]['AWS'] else 0 for b, _ in benchmarks]
    azure_cold = [data_micro[b]['Azure']['avg_cold'] if data_micro[b]['Azure'] else 0 for b, _ in benchmarks]
    azure_warm = [data_micro[b]['Azure']['avg_warm'] if data_micro[b]['Azure'] else 0 for b, _ in benchmarks]

    ax1.bar(x - 1.5*width, aws_cold, width, label='AWS Cold', color=color_map['AWS'], edgecolor='black', linewidth=1)
    ax1.bar(x - 0.5*width, azure_cold, width, label='Azure Cold', color=color_map['Azure'], edgecolor='black', linewidth=1)
    ax1.bar(x + 0.5*width, aws_warm, width, label='AWS Warm', color=color_map['AWS'], alpha=0.5, hatch='///', edgecolor='black', linewidth=1)
    ax1.bar(x + 1.5*width, azure_warm, width, label='Azure Warm', color=color_map['Azure'], alpha=0.5, hatch='///', edgecolor='black', linewidth=1)

    ax1.set_yscale('log')
    ax1.set_xlabel('Microbenchmark', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Execution Time (ms)', fontsize=13, fontweight='bold')
    ax1.set_title('Microbenchmark Performance', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([data_micro[b]['label'] for b, _ in benchmarks], fontsize=11)
    ax1.legend(loc='upper left', fontsize=9, ncol=2)
    ax1.grid(axis='y', alpha=0.3, linestyle='--', which='both')

    # --- Workflows (Right) ---
    workflows = [('620', 'Func-Invo'), ('630', 'Parallel'), ('660', 'Map-Reduce')]

    data_wf = {}
    for wf_id, wf_name in workflows:
        aws_data = load_json(f'../aws_results/experiments_{wf_id}_aws.json')
        azure_data = load_json(f'../azure_results/experiments_{wf_id}.json')

        data_wf[wf_id] = {
            'name': wf_name,
            'AWS': extract_workflow_times(aws_data, wf_id) if aws_data else None,
            'Azure': extract_workflow_times(azure_data, wf_id) if azure_data else None
        }

    x_wf = np.arange(len(workflows))
    width_wf = 0.35

    aws_lat = [data_wf[w]['AWS']['avg_all'] if data_wf[w]['AWS'] else 0 for w, _ in workflows]
    azure_lat = [data_wf[w]['Azure']['avg_all'] if data_wf[w]['Azure'] else 0 for w, _ in workflows]

    bars1 = ax2.bar(x_wf - width_wf/2, aws_lat, width_wf, label='AWS Lambda',
                    color=color_map['AWS'], edgecolor='black', linewidth=1.2)
    bars2 = ax2.bar(x_wf + width_wf/2, azure_lat, width_wf, label='Azure Functions',
                    color=color_map['Azure'], edgecolor='black', linewidth=1.2)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax2.set_xlabel('Workflow Benchmark', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Latency (ms)', fontsize=13, fontweight='bold')
    ax2.set_title('Workflow Performance', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_wf)
    ax2.set_xticklabels([data_wf[w]['name'] for w, _ in workflows], fontsize=11)
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    output_file = '../plots/combined_overview_correct.pdf'
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f" Saved: {output_file}")
    plt.close()

def main():
    """Generate all corrected plots"""
    print("=" * 70)
    print("GENERATING ALL CORRECTED PLOTS WITH PROPER LABELS")
    print("=" * 70)

    import os
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Generate individual plots
    plot_workflow_comparison()
    plot_microbenchmark_comparison()
    plot_combined_overview()

    print("\n" + "=" * 70)
    print(" ALL PLOTS GENERATED SUCCESSFULLY")
    print("=" * 70)
    print("\nOutput files:")
    print("  1. workflow_performance_correct.pdf - Workflow comparison with labels")
    print("  2. microbenchmark_performance_correct.pdf - Function comparison with labels")
    print("  3. combined_overview_correct.pdf - Side-by-side overview")

if __name__ == '__main__':
    main()
