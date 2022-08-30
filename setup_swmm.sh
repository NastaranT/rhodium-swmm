#!/bin/bash

SWMM_REPO_NAME=Stormwater-Management-Model
SWMM_INSTALL_LOCATION=swmm

git clone https://github.com/OpenWaterAnalytics/Stormwater-Management-Model.git

mkdir $SWMM_INSTALL_LOCATION
pushd $SWMM_INSTALL_LOCATION
cmake ../$SWMM_REPO_NAME
make
export PATH=$PATH:$(pwd)/bin
echo $(pwd)
popd
rm -rf $SWMM_REPO_NAME

