#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$script_dir/../.." && pwd)"
cd "$repo_dir/sebs-flow-implementation"

if [[ ! -f python-venv/bin/activate ]]; then
    echo "Set up the implementation virtual environment first." >&2
    exit 1
fi
if [[ ! -f config/azure-test.local.json ]]; then
    echo "Create config/azure-test.local.json with your platform settings first." >&2
    exit 1
fi
source python-venv/bin/activate

for size in test small; do
    python sebs.py benchmark function 050.matrix-multiply "$size" \
        --config config/azure-test.local.json \
        --deployment azure --trigger http \
        --repetitions 15 --language python --verbose
done
