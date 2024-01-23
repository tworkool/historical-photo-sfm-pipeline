# GUIDE

## SETUP

### Setup Conda

`conda env create -f environment.yml`

`conda activate historical-photo-sfm-pipeline`

`sudo apt update`

### Install Colmap

This project uses pycolmap which is a python wrapper for colmap, but it does not support dense MVS reconstruction due to lacking CUDA support, so lets just use the official colmap build.

See file `INSTALL_COLMAP.md` for more info

# Install FFMPEG

if you want to convert your video into single frames you need to download ffmpeg

`sudo apt install ffmpeg`

## RUN

Start Jupyter Lab

`jupyter lab`

Go to `main.ipynb` and go through the cells step by step
