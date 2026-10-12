# SeBS-Flow Replication

Replication of SeBS-Flow benchmarks on AWS Lambda and Azure Functions, with experiment results, plotting scripts, and a matrix multiplication benchmark.

## Contents

| Path | Contents |
| --- | --- |
| [sebs-flow-implementation/](sebs-flow-implementation/) | SeBS-Flow source and benchmark definitions, including local modifications |
| [sebs-flow-artifact/](sebs-flow-artifact/) | Reference measurements, configurations, and analysis from the original artifact |
| [MY_RESEARCH_OUTPUT/](MY_RESEARCH_OUTPUT/) | Replication measurements, analysis, figures, and custom benchmark |
| [report.pdf](report.pdf) | Replication report |
| [presentation.pdf](presentation.pdf) | Presentation PDF |
| [replication_presentation.key](replication_presentation.key) | Editable replication presentation |
| [paper.pdf](paper.pdf) | Reference paper |

## Setup

```bash
git clone --recurse-submodules https://github.com/annamakridou21/SeBS-Flow-Replication.git
cd SeBS-Flow-Replication/sebs-flow-implementation
./install.py --aws --azure --no-gcp --no-openwhisk --no-local
source python-venv/bin/activate
```

Setup requires Python, Docker, and the system dependencies described in the [implementation README](sebs-flow-implementation/README.md#installation). For an existing clone, run `git submodule update --init --recursive` first.

Configure cloud access locally. Copy a platform configuration to a file ending in `.local.json`, fill in the required settings, and use that file for experiments. Workflow measurements also require Redis in the cloud region; see [workflow setup](sebs-flow-implementation/docs/workflows.md).

From `sebs-flow-implementation/`, run a workflow experiment with:

```bash
./sebs.py experiment invoke perf-cost \
  --config config/aws-workflow.local.json \
  --workflow True --output-dir results/my-run --verbose
```

The original experiment configurations are in [sebs-flow-artifact/benchmark-configs/](sebs-flow-artifact/benchmark-configs/). Plotting instructions are in [MY_RESEARCH_OUTPUT/scripts/README.md](MY_RESEARCH_OUTPUT/scripts/README.md).

## Attribution

This project builds on [SeBS](https://github.com/spcl/serverless-benchmarks) and the SeBS-Flow research artifact. The implementation retains its [upstream license](sebs-flow-implementation/LICENSE.md) and [citation](sebs-flow-implementation/CITATION.cff). Reference measurements and replication measurements are kept in separate folders.
