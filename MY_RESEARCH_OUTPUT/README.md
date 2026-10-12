# Replication results

Measurements and analysis from the AWS Lambda and Azure Functions experiments conducted in December 2025.

| Directory | Contents |
| --- | --- |
| `aws_results/` | AWS experiment JSON files |
| `azure_results/` | Azure experiment JSON files |
| `data_analytics/` | Processed CSV tables and structured analysis |
| `analysis_results/` | Analysis summary |
| `supplementary_results/` | Additional measurements and analysis retained from the implementation checkout |
| `plots/` | Comparison and workflow overhead figures |
| `scripts/` | Plot generators |
| `custom_benchmark/` | Matrix multiplication source and local results |

Function measurements cover matrix multiplication, dynamic HTML, thumbnail generation, and compression. Workflow measurements cover function invocation (620), parallel sleep (630), and map-reduce (660).

See the [plotting instructions](scripts/README.md) and [replication report](../report.pdf). Raw experiment files retain invocation details; processed tables and figures may summarize different subsets of those runs. Check the timing field and cold/warm classification before comparing results.
