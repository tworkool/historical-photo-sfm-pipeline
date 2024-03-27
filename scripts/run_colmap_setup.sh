#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: run_colmap_setup.sh <workspace_path> <input_images>"
    exit 1
fi

PROJECT_PATH="${1}"
IMAGE_PATH="${PROJECT_PATH}/image_path"
SPARSE_PATH="${PROJECT_PATH}/sparse"
DB_PATH="${PROJECT_PATH}/database.db"
USE_GPU=1

mkdir -p ${SPARSE_PATH}
mkdir -p ${IMAGE_PATH}

# copy input images to self contained image folder
cp -r "${2}/." "${IMAGE_PATH}"

# Create project directory
#colmap project_generator \
#  --project_path "${WORKSPACE_PATH}" \
#  --output_path "${WORKSPACE_PATH}"

# Create database
colmap database_creator --database_path "$DB_PATH"

# register images and estimate camera parameters
colmap feature_extractor \
    --database_path="${DB_PATH}" \
    --image_path="${IMAGE_PATH}" \
    --ImageReader.camera_model=SIMPLE_RADIAL \
    --ImageReader.single_camera=false \
    --SiftExtraction.use_gpu="${USE_GPU}" \
    --SiftExtraction.num_threads=16 \
    --SiftExtraction.max_image_size=5000 \
    --SiftExtraction.max_num_features=10000

# Perform camera parameter estimation
#colmap mapper --database_path "$DB_PATH" --image_path "$IMAGE_PATH" --output_path "$PROJECT_PATH"

echo "Completed COLMAP Project Setup"