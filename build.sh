#!/bin/bash

# depe
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib

# pico-sdk
git clone https://github.com/raspberrypi/pico-sdk.git
export PICO_SDK_PATH="$(pwd)/pico-sdk"


# build
cd ./firmware/c
mkdir build
cd ./build
cmake -S .. -B .
make
cd -


