#!/bin/bash

# usage: run_colmap_dense_model.sh <project_path>

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <project_path>"
    exit 1
fi

PROJECT_PATH="${1}"
DENSE_MODEL_PATH="${PROJECT_PATH}/dense/delaunay_mesh.ply"

# Perform image undistortion
colmap delaunay_mesher \
  --input_path "$PROJECT_PATH/dense" \
  --output_path "$DENSE_MODEL_PATH" \
  --input_type "dense"
