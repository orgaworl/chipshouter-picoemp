## 使用

物理接线
- picoemp的gpio0引脚连接触发信号
- picoemp的gpio1引脚连接目标设备的复位引脚

工具使用
需要根据目标设备串口的不同类型响应修改代码，例如当目标设备复位返回 "RESET" 、控制流被打断时返回含有 "(" 的字符串，则修改以下内容:
```python
class StatusString:
    SUCCESS="("
    RESET="RESET"
```