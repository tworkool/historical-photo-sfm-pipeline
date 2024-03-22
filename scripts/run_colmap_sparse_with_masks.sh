#!/bin/bash

# usage: run_colmap_sparse_with_masks.sh <project_path> <images_path> <mask_path>

if [ "$#" -ne 3 ]; then
    echo "ERROR: 2 arguments are required, usage: $0 <project_path> <images_path> <mask_path>"
    exit 1
fi

image_path="${1}/image_path"
mask_path="${1}/mask_path"
sparse_path="${1}/sparse"
db_path="${1}/database.db"
use_gpu=false

mkdir -p ${sparse_path}
mkdir -p ${image_path}
mkdir -p ${mask_path}

# copy input images to self contained image folder
cp ${2}/* ${image_path}
cp ${3}/* ${mask_path}

colmap feature_extractor \
    --database_path="${db_path}" \
    --image_path="${image_path}" \
    --ImageReader.camera_model=SIMPLE_RADIAL \
    --ImageReader.single_camera=false \
    --SiftExtraction.use_gpu="${use_gpu}" \
    --SiftExtraction.num_threads=32 \
    --SiftExtraction.max_image_size=5000 \
    --SiftExtraction.max_num_features=10000

colmap sequential_matcher \
    --database_path="${db_path}" \
    --SiftMatching.use_gpu="${use_gpu}"

colmap mapper \
    --database_path="${db_path}" \
    --image_path="${image_path}" \
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
