# 2. Run iCatcher+

## Quick Start

1. Navigate to this directory: `cd preprocessing/2_run_icatcher`
2. Activate the conda environment: `conda activate visualprecision`
3. Check which GPU is available: `nvidia-smi`
4. Run the pipeline: `python run_icatcher_local.py --gpu_id 0`

If you run into any issues with CUDA, PyTorch, or GPU errors, see the [Troubleshooting & Setup Details](#troubleshooting--setup-details) section below.

---

## Troubleshooting & Setup Details

### Python & PyTorch Requirements
The `visualprecision` environment must use **Python 3.11**. PyTorch does not currently support Python 3.13, so do not run this in the base conda environment.

To verify your setup:
```bash
python --version                                             # should be 3.11.x
python -c "import torch; print(torch.cuda.is_available())"  # should print True
```

### Matching PyTorch to the Server's CUDA Version
PyTorch must be compiled for the correct CUDA version or the GPU will not be detected. On **Tversky**, the driver supports CUDA 12.2, so install:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```
To check the server's CUDA version at any time: `nvidia-smi`

### Choosing the Right GPU ID
Always check which GPUs are available before running:
```bash
nvidia-smi
```
Then pass the correct ID:
```bash
python run_icatcher_local.py --gpu_id 0
```
Using an ID that doesn't exist (e.g. `--gpu_id 1` when only GPU 0 is available) will throw `RuntimeError: CUDA error: invalid device ordinal`.

### Running with SBATCH
To submit as a job on the cluster instead:
```bash
bash run_icatcher_job_array.sh
```

### CPU Mode
The current pipeline does not support CPU use, but in theory this is possible with modifications to the script.