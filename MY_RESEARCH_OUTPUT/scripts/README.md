# Plotting

Install the plotting dependencies from the repository root:

```bash
python3 -m pip install -r MY_RESEARCH_OUTPUT/scripts/requirements.txt
```

Generate figures with:

```bash
python3 MY_RESEARCH_OUTPUT/scripts/generate_all_correct_plots.py
python3 MY_RESEARCH_OUTPUT/scripts/generate_correct_workflow_plots.py
python3 MY_RESEARCH_OUTPUT/scripts/generate_overhead_plots.py
```

| Script | Output |
| --- | --- |
| `generate_all_correct_plots.py` | Function, workflow, and combined comparison PDFs |
| `generate_correct_workflow_plots.py` | Cold/warm, three-panel, and distribution PDFs |
| `generate_overhead_plots.py` | Individual and combined workflow overhead PDFs |

Inputs are the JSON files in `../aws_results/` and `../azure_results/`. Figures are saved to `../plots/`. Paths are resolved relative to the scripts, so these commands work from any directory.

The comparison scripts use `client` timing for workflows on both platforms, converted from microseconds to milliseconds. The overhead script compares `client` and `benchmark` timings and estimates Azure map-reduce's critical path as 85% of total time. Treat that decomposition as an estimate. Stored figures are retained from the experiment period; regenerating them may produce different output.
