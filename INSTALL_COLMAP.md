# colmap dependencies
```
sudo apt-get update

sudo apt-get install -y \
    git \
    cmake \
    ninja-build \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev
```

# headless servers
```
sudo apt-get install -y \
    xvfb
```

# Colmap
```
mkdir third_party
cd third_party
git clone https://github.com/colmap/colmap.git colmap
cd colmap
git checkout release/3.9
mkdir build 
cd build 
cmake .. -DCUDA_ENABLED=ON -DCMAKE_CUDA_ARCHITECTURES="70;72;75;80;86" -GNinja
sudo ninja
sudo ninja install
```