#!/bin/bash

# usage: run_colmap_sparse.sh <project_path> <images_path>

if [ "$#" -ne 2 ]; then
    echo "ERROR: 2 arguments are required, usage: $0 <project_path> <images_path>"
    exit 1
fi

image_path="${1}/images_raw"
sparse_path="${1}/sparse"
db_path="${1}/database.db"
use_gpu=true

mkdir -p ${sparse_path}
mkdir -p ${image_path}

# copy input images to self contained image folder
cp ${2}/* ${image_path}

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
    
