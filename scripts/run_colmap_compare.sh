#!/bin/bash
# usage: run_colmap_compare.sh <in1> <in2>
# bash run_colmap_compare.sh "/mnt/c/Users/tworkool/Documents/dev/python/historical-photo-sfm-pipeline/data/3_results/3_koepenick_rathaus_SfM/sparse" "/mnt/c/Users/tworkool/Documents/dev/python/historical-photo-sfm-pipeline/data/3_results/3_koepenick_rathaus_SfM_werramat/sparse"

if [ "$#" -ne 2 ]; then
    echo "ERROR: 2 arguments are required, usage: $0 <in1> <in2>"
    exit 1
fi

out_path="${1}/compare"
mkdir -p ${out_path}

colmap model_comparer \
  --input_path1 "${1}" \
  --input_path2 "${2}" \
  --output_path "${out_path}" \
  #--log_to_stderr arg (=1) \
  #--log_level arg (=0) \
  #--project_path arg
  #--alignment_error arg (=reprojection) {reprojection, proj_center}
  #--min_inlier_observations arg (=0.29999999999999999)
  #--max_reproj_error arg (=8)
  #--max_proj_center_error arg (=0.10000000000000001)
