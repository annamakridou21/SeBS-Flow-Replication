#!/usr/bin/env python3
"""
Generate correct workflow plots using actual JSON data
Creates three visualizations:
1. Cold vs Warm comparison (first plot style)
2. Three-panel detailed breakdown (second plot style)
3. Box plot distribution (third plot style)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from pathlib import Path

# Set publication style
sb.set_theme()
sb.set_context("paper", font_scale=1.2)
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

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

def extract_workflow_times(data):
    """Extract cold and warm start times from workflow results

    CRITICAL: Always use 'client' time for workflows!
    - AWS workflows: client time = end-to-end orchestration
    - Azure workflows: client time = end-to-end orchestration
    - Do NOT use 'benchmark' field - it's not the orchestration time
    """
    if not data or '_invocations' not in data:
        return None

    cold_times = []
    warm_times = []
    all_times = []

    # Get first key (workflow name)
    workflow_key = list(data['_invocations'].keys())[0]
    invocations = data['_invocations'][workflow_key]

    for req_id, invocation in invocations.items():
        if 'times' in invocation and 'client' in invocation['times']:
            # ALWAYS use client time for workflows (both AWS and Azure)
            # Times are in microseconds, convert to milliseconds
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

def plot_cold_warm_comparison():
    """Create cold vs warm start comparison plot"""

    workflows = ['Func-Invo', 'Parallel-Sleep', 'Map-Reduce']
    workflow_ids = ['620', '630', '660']

    # Load all data
    print("\n=== Loading Workflow Data ===")
    data = {}
    for wf_name, wf_id in zip(workflows, workflow_ids):
        aws_file = f'../azure_results/experiments_{wf_id}_aws.json'
        azure_file = f'../azure_results/experiments_{wf_id}.json'

        # Try alternate locations
        if not Path(aws_file).exists():
            aws_file = f'../aws_results/experiments_{wf_id}_aws.json'

        aws_data = load_json(aws_file)
        azure_data = load_json(azure_file)

        aws_times = extract_workflow_times(aws_data)
        azure_times = extract_workflow_times(azure_data)

        data[wf_name] = {
            'AWS': aws_times,
            'Azure': azure_times
        }

        # Print summary
        print(f"\n{wf_name} ({wf_id}):")
        if aws_times:
            print(f"  AWS - Cold: {aws_times['avg_cold']:.1f}ms, Warm: {aws_times['avg_warm']:.1f}ms, Overall: {aws_times['avg_all']:.1f}ms")
        if azure_times:
            print(f"  Azure - Cold: {azure_times['avg_cold']:.1f}ms, Warm: {azure_times['avg_warm']:.1f}ms, Overall: {azure_times['avg_all']:.1f}ms")

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(workflows))
    width = 0.35

    # Prepare data for plotting
    aws_cold = []
    aws_warm = []
    azure_cold = []
    azure_warm = []

    for wf in workflows:
        if data[wf]['AWS']:
            aws_cold.append(data[wf]['AWS']['avg_cold'] / 1000)  # Convert to seconds
            aws_warm.append(data[wf]['AWS']['avg_warm'] / 1000)
        else:
            aws_cold.append(0)
            aws_warm.append(0)

        if data[wf]['Azure']:
            azure_cold.append(data[wf]['Azure']['avg_cold'] / 1000)
            azure_warm.append(data[wf]['Azure']['avg_warm'] / 1000)
        else:
            azure_cold.append(0)
            azure_warm.append(0)

    # Plot bars
    ax.bar(x - width/2, aws_cold, width/2, label='AWS', color=color_map['AWS'], alpha=1.0)
    ax.bar(x - width/2, aws_warm, width/2, bottom=aws_cold, color=color_map['AWS'], alpha=0.5, hatch='///')

    ax.bar(x + width/2, azure_cold, width/2, label='Azure', color=color_map['Azure'], alpha=1.0)
    ax.bar(x + width/2, azure_warm, width/2, bottom=azure_cold, color=color_map['Azure'], alpha=0.5, hatch='///')

    # Formatting
    ax.set_xlabel('Workflow Benchmark', fontsize=13, fontweight='bold')
    ax.set_ylabel('Duration [s]', fontsize=13, fontweight='bold')
    ax.set_title('Workflow Performance: Cold Start vs Warm Start', fontsize=15, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(workflows)
    ax.set_ylim(0, max(max(azure_cold), max(azure_warm)) * 1.1)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color_map['AWS'], label='AWS'),
        Patch(facecolor=color_map['Azure'], label='Azure'),
        Patch(facecolor='gray', label='Cold Start'),
        Patch(facecolor='gray', alpha=0.5, hatch='///', label='Warm Start')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

    plt.tight_layout()
    output_file = '../plots/workflow_cold_warm_correct.pdf'
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f"\n Saved: {output_file}")
    plt.close()

def plot_three_panel_breakdown():
    """Create three-panel detailed breakdown"""

    workflows = [('Func-Invo', '620'), ('Parallel-Sleep', '630'), ('Map-Reduce', '660')]

    # Load data
    data = {}
    for wf_name, wf_id in workflows:
        aws_file = f'../azure_results/experiments_{wf_id}_aws.json'
        azure_file = f'../azure_results/experiments_{wf_id}.json'

        if not Path(aws_file).exists():
            aws_file = f'../aws_results/experiments_{wf_id}_aws.json'

        aws_data = load_json(aws_file)
        azure_data = load_json(azure_file)

        data[wf_name] = {
            'AWS': extract_workflow_times(aws_data),
            'Azure': extract_workflow_times(azure_data)
        }

    # Create three-panel figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for idx, (wf_name, wf_id) in enumerate(workflows):
        ax = axes[idx]

        platforms = ['AWS', 'Azure']
        x_pos = np.arange(len(platforms))

        cold_vals = []
        warm_vals = []
        cold_stds = []
        warm_stds = []

        for platform in platforms:
            if data[wf_name][platform]:
                d = data[wf_name][platform]
                cold_vals.append(d['avg_cold'] / 1000)  # Convert to seconds
                warm_vals.append(d['avg_warm'] / 1000)
                cold_stds.append(np.std(d['cold']) / 1000 if d['cold'] else 0)
                warm_stds.append(np.std(d['warm']) / 1000 if d['warm'] else 0)
            else:
                cold_vals.append(0)
                warm_vals.append(0)
                cold_stds.append(0)
                warm_stds.append(0)

        width = 0.35

        # Plot bars with error bars
        bars1 = ax.bar(x_pos, cold_vals, width, label='Cold Start',
                       color=[color_map['AWS'], color_map['Azure']],
                       alpha=1.0, edgecolor='black', linewidth=0.8)
        bars2 = ax.bar(x_pos, warm_vals, width, bottom=cold_vals, label='Warm Start',
                       color=[color_map['AWS'], color_map['Azure']],
                       alpha=0.5, hatch='///', edgecolor='black', linewidth=0.8)

        # Add value labels
        for i, (c, w) in enumerate(zip(cold_vals, warm_vals)):
            total = c + w
            if total > 0:
                ax.text(i, total + max(cold_vals) * 0.05, f'{total:.1f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Formatting
        ax.set_ylabel('Duration [s]', fontsize=11)
        ax.set_title(f'({chr(97+idx)}) {wf_name}', fontsize=12, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(platforms)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        if idx == 2:
            ax.legend(loc='upper left', fontsize=9)

    plt.suptitle('Workflow Performance: Cold Start vs Warm Start', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_file = '../plots/workflow_three_panel_correct.pdf'
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f" Saved: {output_file}")
    plt.close()

def plot_box_distributions():
    """Create box plot showing distributions"""

    workflows = [('Func-Invo', '620'), ('Parallel-Sleep', '630'), ('Map-Reduce', '660')]

    # Load data
    data = {}
    for wf_name, wf_id in workflows:
        aws_file = f'../azure_results/experiments_{wf_id}_aws.json'
        azure_file = f'../azure_results/experiments_{wf_id}.json'

        if not Path(aws_file).exists():
            aws_file = f'../aws_results/experiments_{wf_id}_aws.json'

        aws_data = load_json(aws_file)
        azure_data = load_json(azure_file)

        data[wf_name] = {
            'AWS': extract_workflow_times(aws_data),
            'Azure': extract_workflow_times(azure_data)
        }

    # Create three-panel figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for idx, (wf_name, wf_id) in enumerate(workflows):
        ax = axes[idx]

        # Prepare data for box plot
        aws_times = data[wf_name]['AWS']['all'] if data[wf_name]['AWS'] else []
        azure_times = data[wf_name]['Azure']['all'] if data[wf_name]['Azure'] else []

        # Convert to seconds
        aws_times_s = [t/1000 for t in aws_times]
        azure_times_s = [t/1000 for t in azure_times]

        # Create box plot
        positions = [0, 1]
        bp = ax.boxplot([aws_times_s, azure_times_s], positions=positions,
                        widths=0.6, patch_artist=True,
                        showfliers=True, showmeans=False)

        # Color boxes
        bp['boxes'][0].set_facecolor(color_map['AWS'])
        bp['boxes'][1].set_facecolor(color_map['Azure'])

        for box in bp['boxes']:
            box.set_edgecolor('black')
            box.set_linewidth(1.5)

        # Add mean values as text
        if aws_times_s:
            ax.text(0, max(aws_times_s) * 1.05, f'{np.mean(aws_times_s):.2f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black'))
        if azure_times_s:
            ax.text(1, max(azure_times_s) * 1.05, f'{np.mean(azure_times_s):.2f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black'))

        # Formatting
        ax.set_ylabel('Duration [s]', fontsize=11)
        ax.set_title(f'({chr(97+idx)}) {wf_name}', fontsize=12, fontweight='bold')
        ax.set_xticks(positions)
        ax.set_xticklabels(['AWS', 'Azure'])
        ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.suptitle('Workflow Performance Distribution', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_file = '../plots/workflow_box_plot_correct.pdf'
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f" Saved: {output_file}")
    plt.close()

def main():
    """Generate all corrected workflow plots"""
    print("=" * 60)
    print("GENERATING CORRECTED WORKFLOW PLOTS FROM JSON DATA")
    print("=" * 60)

    # Change to script directory
    import os
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Generate all plots
    plot_cold_warm_comparison()
    plot_three_panel_breakdown()
    plot_box_distributions()

    print("\n" + "=" * 60)
    print(" ALL PLOTS GENERATED SUCCESSFULLY")
    print("=" * 60)
    print("\nOutput files:")
    print("  1. workflow_cold_warm_correct.pdf")
    print("  2. workflow_three_panel_correct.pdf")
    print("  3. workflow_box_plot_correct.pdf")

if __name__ == '__main__':
    main()
