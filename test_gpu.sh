#!/bin/bash
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH

# Find site-packages
SITE_PACKAGES="venv/lib/python3.10/site-packages"

# Loop and add all installed nvidia/lib folders to LD_LIBRARY_PATH
for dir in $SITE_PACKAGES/nvidia/*/lib; do
    if [ -d "$dir" ]; then
        export LD_LIBRARY_PATH="$dir:$LD_LIBRARY_PATH"
    fi
done

echo "Running TensorFlow GPU check..."
venv/bin/python -c "import tensorflow as tf; print('GPUs found:', tf.config.list_physical_devices('GPU'))"
