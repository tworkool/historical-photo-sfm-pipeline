#!/bin/bash

# usage: run_colmap_sparse.sh <project_path> <images_path>

if [ "$#" -ne 2 ]; then
    echo "ERROR: 2 arguments are required, usage: $0 <project_path> <images_path>"
    exit 1
fi

sparse_path="${1}/sparse"
db_path="${1}/database.db"
use_gpu=false

mkdir -p ${sparse_path}

colmap mapper \
    --database_path="${db_path}" \
    --image_path="${2}" \
    --output_path="${sparse_path}"

cp "${sparse_path}/0"/*.bin "${sparse_path}/"
for path in $(find "${sparse_path}" -type d); do
    m=$(basename "${path}")
    if [ "${m}" != "0" ]; then
        colmap model_merger \
            --input_path1="${sparse_path}" \
            --input_path2="${sparse_path}/${m}" \
            --output_path="${sparse_path}"
    fi
done


colmap bundle_adjuster \
    --input_path="${sparse_path}" \
    --output_path="${sparse_path}"
