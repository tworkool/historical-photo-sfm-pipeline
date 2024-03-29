#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: run_colmap_setup.sh <workspace_path>"
    exit 1
fi

PROJECT_PATH="${1}"
SPARSE_PATH="${PROJECT_PATH}/sparse"
MODEL_PATH="${SPARSE_PATH}/model.ply"

colmap model_converter \
	--input_path "$SPARSE_PATH" \
	--output_path "$MODEL_PATH" \
	--output_type "PLY"

echo "----- Completed COLMAP Sparse Reconstruction Export -----"