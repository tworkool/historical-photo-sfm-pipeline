#!/bin/bash

# usage: run_colmap_sparse_cleanup.sh <project_path>

if [ "$#" -ne 1 ]; then
    echo "ERROR: 2 arguments are required, usage: $0 <project_path>"
    exit 1
fi

IMAGE_PATH="${1}/image_path"
SPARSE_PATH="${1}/sparse"
DB_PATH="${1}/database.db"
FILTERED_SPARSE_PATH="${SPARSE_PATH}/filtered"

mkdir -p ${FILTERED_SPARSE_PATH}

colmap point_filtering \
    --input_path "${SPARSE_PATH}" \
    --output_path "${FILTERED_SPARSE_PATH}"
