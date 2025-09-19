
# 编译

安装工具链
```shell
# depe
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib
```

下载树莓派 pico sdk
```shell
# pico-sdk
cd ./c
git clone https://github.com/raspberrypi/pico-sdk.git
export PICO_SDK_PATH="$(pwd)/pico-sdk"
```

开始编译
```shell
# build
mkdir build
cd ./build
cmake -S .. -B .
make
```

随后可在build文件夹下找到多种类型的固件，一般选择 uf2 类型的固件进行烧录。
- picoemp.bin
- picoemp.elf
- picoemp.hex
- picoemp.uf2


# 使用说明

## 代码已修改部分
- 关闭自动休眠
- 将所有参数的配置同意聚合到命令 `c` 上

## 可配置参数

- pulse_time 默认5(us)
- pulse_power 默认0.0122
- pulse_delay_cycles 默认0 cycles (1 cycle=8ns)
- pulse_time_cycles 默认625 cycles
- HVP 可配置为HVP internal 或HVP external


## 外部引脚
- gpio0 触发输入引脚
- gpio1 用以复位目标设备，通过反转实现复位

## 自动化攻击

见 `picoemp_auto_attack`