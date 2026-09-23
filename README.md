# HJ212-Lab —— HW1 实验一：Git 与 hj212parser 类库

HW1 实验一的代码仓库：git 基本操作练习 + HJ212-2017 环保协议解析类库。

## 目录结构

```
HJ212-Lab/
├── src/
│   ├── helloworld.py      # 实验内容 2-(1)：HelloWorld 程序
│   └── hj212parser.py     # 实验内容 2-(2)：HJ212-2017 协议解析类库
├── tests/
│   └── test_hj212parser.py# hj212parser 单元测试（12 个用例）
├── docs/
│   └── 运行示例.txt        # 程序运行输出记录
├── .gitignore
└── README.md
```

## 快速开始

```bash
# 运行 HelloWorld
python src/helloworld.py

# 运行 hj212parser 示例
python src/hj212parser.py

# 运行单元测试
python tests/test_hj212parser.py
```

## hj212parser 使用示例

```python
from hj212parser import HJ212Parser, build_message

segment = ("ST=32;CN=2011;PW=123456;MN=88888880000001;Flag=3;"
           "CP=&&DataTime=20240101120000;w01018-Rtd=7.5&&")
msg = build_message(segment)          # 自动计算长度和 CRC16

p = HJ212Parser()
p.is_valid_message(msg)               # 报文格式合法性校验 -> True
p.validate_crc(msg)                   # CRC16 校验 -> True
p.parse_data_segment(msg)             # 解析数据段 -> {'ST': '32', ..., 'CP': {...}}
p.extract_monitoring_data(msg)        # 提取监测因子数据 -> {'DataTime': ..., 'w01018-Rtd': '7.5'}
```

## 实现的功能

1. `is_valid_message(message)` —— 报文格式合法性校验（起始符/长度字段/数据段结构/CRC）
2. `validate_crc(message)` —— 基于 ANSI CRC16（多项式 0xA001，初值 0xFFFF）校验报文 CRC
3. `parse_data_segment(message)` —— 解析数据段，返回包含所有键值的字典（CP 子段解析为嵌套字典）
4. `extract_monitoring_data(message)` —— 提取 CP=&&...&& 中的监测因子实时数据字典
