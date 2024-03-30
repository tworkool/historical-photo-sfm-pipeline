#!/bin/bash

# usage: run_colmap_dense.sh <project_path>

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <project_path>"
    exit 1
fi

project_path="${1}"
image_path="${project_path}/image_path"
sparse_path="${project_path}/sparse"
dense_path="${project_path}/dense"
db_path="${project_path}/database.db"

# Check if directories exist
if [ ! -d "${image_path}" ]; then
    echo "Error: Directory '${image_path}' not found."
    exit 1
fi

if [ ! -d "${sparse_path}" ]; then
    echo "Error: Directory '${sparse_path}' not found."
    exit 1
fi

if [ ! -f "${db_path}" ]; then
    echo "Error: Database file '${db_path}' not found."
    exit 1
fi

# Create necessary directories
mkdir -p "${dense_path}"

# Perform image undistortion
colmap image_undistorter \
    --image_path="${image_path}" \
    --input_path="${sparse_path}" \
    --output_path="${dense_path}" \
    --output_type=COLMAP

# Perform patch match stereo
colmap patch_match_stereo \
    --workspace_path="${dense_path}" \
    --workspace_format=COLMAP \
    --PatchMatchStereo.max_image_size=3000 \
    --PatchMatchStereo.num_samples=20 \
    --PatchMatchStereo.geom_consistency=1 \
    --PatchMatchStereo.geom_consistency_regularizer=1 \
    --PatchMatchStereo.filter_min_num_consistent=0 \
    --PatchMatchStereo.filter_min_triangulation_angle=0 \
    --PatchMatchStereo.incident_angle_sigma=1 \
    --PatchMatchStereo.filter_min_ncc=0 \
    --PatchMatchStereo.num_iterations=5

# Perform stereo fusion
colmap stereo_fusion \
    --workspace_path="${dense_path}" \
    --workspace_format=COLMAP \
    --output_path="${dense_path}/fused.ply" \
    --StereoFusion.max_num_pixels=10000000 \
    --StereoFusion.max_normal_error=1000000 \
    --StereoFusion.max_reproj_error=3
