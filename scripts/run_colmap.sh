# usage: run_colmap.sh <project_path> <images_path>

if [ "$#" -ne 2 ]; then
    echo "ERROR: 2 arguments are required, usage: $0 <project_path> <images_path>"
    exit 1
fi

bash run_colmap_sparse.sh "${1}" "${2}"
bash run_colmap_dense.sh "${1}"
