#!/bin/bash

# usage: run_colmap_dense_mesh.sh <project_path> <mesh_type>

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <project_path> <mesh_type>"
  echo "<mesh_type> should be either 'delaunay' or 'poisson'"
  exit 1
fi

PROJECT_PATH="${1}"
MESH_TYPE="${2}"
DENSE_PATH="${PROJECT_PATH}/dense"
DENSE_RECONSTRUCTION_PATH="${DENSE_PATH}/fused.ply"

# Perform image undistortion based on mesh type
if [ "${MESH_TYPE}" = "poisson" ]; then
    if [ ! -f "${DENSE_RECONSTRUCTION_PATH}" ]; then
      echo "Error: dense reconstruction file '${DENSE_RECONSTRUCTION_PATH}' not found. Please run a dense reconstruction first, before this script can create a model."
      exit 1
    fi
    colmap poisson_mesher \
      --input_path "$DENSE_RECONSTRUCTION_PATH" \
      --output_path "${DENSE_PATH}/poisson_mesh.ply" 
elif [ "${MESH_TYPE}" = "delaunay" ]; then
    colmap delaunay_mesher \
      --input_path "$DENSE_PATH" \
      --output_path "${DENSE_PATH}/delaunay_mesh.ply"  \
      --input_type "dense"
else
    echo "Error: <mesh_type> must be 'delaunay' or 'poisson'"
    exit 1
fi
