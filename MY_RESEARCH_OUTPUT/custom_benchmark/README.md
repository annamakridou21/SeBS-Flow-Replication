# Matrix multiplication benchmark

The Python function uses NumPy to multiply randomly initialized square matrices and returns the size, diagonal checksum, and compute time. Input sizes range from 1 to 1000; `input.py` supplies the requested matrix size.

`matrix_mult.c` is a standalone C example that multiplies two fixed 100-by-100 matrices. It is not a deployed serverless runtime. Compile and run it locally with:

```bash
cd MY_RESEARCH_OUTPUT/custom_benchmark
cc -O2 -std=c99 matrix_mult.c -o matrix_mult
./matrix_mult
```

`config.json` declares Python support, a 30-second timeout, and 256 MB of memory. `workflow.json` contains a single task definition.

The launch scripts run the Python `050.matrix-multiply` benchmark in the implementation directory with test and small inputs. Configure cloud access and prepare the implementation virtual environment before using them:

```bash
bash MY_RESEARCH_OUTPUT/custom_benchmark/run_aws_benchmark.sh
bash MY_RESEARCH_OUTPUT/custom_benchmark/run_azure_benchmark.sh
```

Both scripts require a platform configuration ending in `.local.json`. AWS uses `config/aws-test.local.json`; Azure uses `config/azure-test.local.json`. The JSON files in `results/` retain local experiment output. AWS and Azure matrix multiplication measurements are also available in the platform result directories.
