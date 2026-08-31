#!/bin/bash
set -e

# Use F drive
export TMPDIR=/mnt/f/emotion-detection/pip_tmp
export PIP_CACHE_DIR=/mnt/f/emotion-detection/pip_cache

echo "Installing exact CUDA/cuDNN versions compatible with TF 2.15..."
venv/bin/pip install --force-reinstall \
    nvidia-cuda-runtime-cu12==12.2.140 \
    nvidia-cublas-cu12==12.2.5.6 \
    nvidia-cufft-cu12==11.0.8.103 \
    nvidia-cudnn-cu12==8.9.4.25 \
    nvidia-cusolver-cu12==11.5.2.141 \
    nvidia-cusparse-cu12==12.1.2.141 \
    nvidia-cuda-cupti-cu12==12.2.142 \
    nvidia-nccl-cu12==2.16.5 \
    nvidia-nvjitlink-cu12==12.2.140 \
    nvidia-cuda-nvrtc-cu12==12.2.140

echo "Exact CUDA versions installed successfully!"
