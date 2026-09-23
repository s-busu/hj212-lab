# -*- coding: utf-8 -*-
"""
hj212parser —— 用于解析 HJ212-2017 环保数据传输协议报文的 Python 类库

报文结构：##{长度}{数据段}{CRC16}\r\n
    - ##          : 起始符
    - 长度        : 4 位十进制数字，表示数据段的长度（ASCII 字符数）
    - 数据段      : 形如 "ST=32;CN=2011;PW=123456;MN=88888880000001;Flag=3;
                    CP=&&DataTime=20240101120000;w01018-Rtd=7.5&&" 的键值对串
    - CRC16       : 4 位大写十六进制，基于 ANSI CRC-16（多项式 0xA001，初值 0xFFFF），
                    对数据段计算
    - \r\n        : 结束符

作者：XXX（学号：XXXXXXXX）   实验一 HW1
"""

# HJ212-2017 中常用的系统编码 / 命令编号仅供注释参考，不做硬编码校验
# ST: 系统编码  CN: 命令编码  PW: 密码  MN: 设备唯一标识  Flag: 标志位  CP: 参数/数据

CRC16_POLY = 0xA001     # ANSI CRC16 多项式（反转形式，等价于 0x8005）
CRC16_INIT = 0xFFFF     # CRC 初值（补码取反，即先取反再运算，XOR 0xFFFF）


class HJ212Parser(object):
    """HJ212-2017 协议报文解析器"""

    # ------------------------------------------------------------------
    # CRC16 校验
    # ------------------------------------------------------------------
    @staticmethod
    def compute_crc(data):
        """对字符串 data 计算 ANSI CRC16（多项式 0xA001，初值 0xFFFF）。

        返回 4 位大写十六进制字符串。
        """
        crc = CRC16_INIT  # 初值 0xFFFF（补码取反）
        for ch in data.encode("utf-8"):
            crc ^= ch
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ CRC16_POLY
                else:
                    crc >>= 1
        return "{:04X}".format(crc & 0xFFFF)

    def validate_crc(self, message):
        """校验报文中的 CRC16 是否正确，正确返回 True，否则 False。

        message: 完整报文字符串（可含或不含结尾 \\r\\n）。
        """
        body = self._strip_frame(message)
        if body is None or len(body) < 12:
            return False
        data_segment = body[4:-4]   # 跳过 4 位长度字段，去掉末尾 4 位 CRC
        crc_in_msg = body[-4:]
        return self.compute_crc(data_segment) == crc_in_msg.upper()

    # ------------------------------------------------------------------
    # 报文格式合法性校验
    # ------------------------------------------------------------------
    def is_valid_message(self, message):
        """校验 HJ212-2017 报文格式是否合法。

        合法条件：
          1. 以 "##" 开头，以 "\\r\\n" 结尾（允许传入时省略结尾符）；
          2. "##" 之后紧跟 4 位十进制数字的长度字段；
          3. 长度字段的数值 == 数据段的实际长度；
          4. 报文以 4 位十六进制 CRC16 结尾且 CRC 校验通过；
          5. 数据段的基本结构合法（含键值对）。
        """
        if not isinstance(message, str) or len(message) < 12:
            return False

        if message.endswith("\r\n"):
            message = message[:-2]

        if not message.startswith("##"):
            return False

        body = message[2:]
        if len(body) < 4 + 4:          # 长度4位 + 至少1字段键值 + CRC4位
            return False

        length_field = body[:4]
        if not length_field.isdigit():
            return False

        data_segment = body[4:-4]
        crc_field = body[-4:]

        # 长度校验
        if int(length_field) != len(data_segment):
            return False

        # CRC 字段必须是 4 位十六进制
        try:
            int(crc_field, 16)
        except ValueError:
            return False

        # CRC 校验
        if self.compute_crc(data_segment) != crc_field.upper():
            return False

        # 数据段基本结构校验：至少包含一个合法的 "K=V" 对
        return self._check_segment_structure(data_segment)

    def _check_segment_structure(self, data_segment):
        """校验数据段的键值对结构是否基本合法。"""
        # 拆出 CP=&&...&& 部分，其余按 ';' 分隔
        head = data_segment
        cp_dict = None
        idx = data_segment.find("CP=&&")
        if idx != -1:
            end = data_segment.find("&&", idx + 5)
            if end == -1:
                return False
            head = (data_segment[:idx] + data_segment[end + 2:]).strip(";")
            cp_dict = data_segment[idx + 5:end]

        if head == "" and cp_dict is None:
            return False

        for pair in head.split(";"):
            if pair == "":
                continue
            if "=" not in pair:
                return False
            k, v = pair.split("=", 1)
            if k == "" or v == "":
                return False

        if cp_dict is not None:
            for pair in cp_dict.split(";"):
                if pair == "":
                    continue
                if "=" not in pair:
                    return False
        return True

    # ------------------------------------------------------------------
    # 数据段解析
    # ------------------------------------------------------------------
    def parse_data_segment(self, message):
        """解析报文数据段，返回包含所有传输数据键值的字典。

        普通字段（ST/CN/PW/MN/Flag 等）直接作为字典的键值对；
        CP=&&...&& 中的内容解析为嵌套字典，键为 "CP"。
        """
        body = self._strip_frame(message)
        if body is None:
            raise ValueError("报文格式非法，无法解析数据段")
        data_segment = body[4:-4]
        return self._parse_pairs(data_segment)

    def extract_monitoring_data(self, message):
        """从 HJ212 报文中提取监测因子数据的字典。

        即提取 CP=&&...&& 内的实时数据，例如：
            {"DataTime": "20240101120000", "w01018-Rtd": "7.5", ...}
        若报文不含 CP 数据段，则返回空字典。
        """
        try:
            parsed = self.parse_data_segment(message)
        except ValueError:
            return {}
        cp_value = parsed.get("CP")
        if isinstance(cp_value, dict):
            return cp_value
        return {}

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------
    @staticmethod
    def _strip_frame(message):
        """去掉报文的 '##'、4 位长度字段、CRC 与结尾 \\r\\n，返回中间主体。

        返回形如 '{长度}{数据段}{CRC}' 的字符串；非法报文返回 None。
        """
        if not isinstance(message, str):
            return None
        if message.endswith("\r\n"):
            message = message[:-2]
        if not message.startswith("##") or len(message) < 2 + 4 + 4:
            return None
        return message[2:]

    @staticmethod
    def _parse_pairs(segment):
        """将键值对串解析为字典；CP=&&...&& 解析为嵌套字典。"""
        result = {}
        head_pairs = []

        idx = segment.find("CP=&&")
        if idx != -1:
            end = segment.find("&&", idx + 5)
            cp_content = segment[idx + 5:end] if end != -1 else segment[idx + 5:]
            cp_dict = {}
            for pair in cp_content.split(";"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    cp_dict[k] = v
            rest = (segment[:idx] if end == -1 else segment[:idx] + segment[end + 2:])
            head_pairs.append(("CP", cp_dict))
            head_pairs.extend(HJ212Parser._split_kv(rest.strip(";")))
        else:
            head_pairs = HJ212Parser._split_kv(segment)

        for k, v in head_pairs:
            result[k] = v
        return result

    @staticmethod
    def _split_kv(segment):
        pairs = []
        for pair in segment.split(";"):
            if pair and "=" in pair:
                k, v = pair.split("=", 1)
                pairs.append((k, v))
        return pairs


# ----------------------------------------------------------------------
# 报文构造辅助函数（用于测试与示例）
# ----------------------------------------------------------------------
def build_message(data_segment):
    """根据数据段构造完整的 HJ212-2017 报文（含长度、CRC、\\r\\n）。"""
    crc = HJ212Parser.compute_crc(data_segment)
    return "##{:04d}{}{}\r\n".format(len(data_segment), data_segment, crc)


if __name__ == "__main__":
    # 简单示例
    sample = build_message(
        "ST=32;CN=2011;PW=123456;MN=88888880000001;Flag=3;"
        "CP=&&DataTime=20240101120000;w01018-Rtd=7.5;w01018-Flag=N&&"
    )
    parser = HJ212Parser()
    print("报文:", sample)
    print("格式合法:", parser.is_valid_message(sample))
    print("CRC正确:", parser.validate_crc(sample))
    print("数据段:", parser.parse_data_segment(sample))
    print("监测数据:", parser.extract_monitoring_data(sample))
