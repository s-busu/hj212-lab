# -*- coding: utf-8 -*-
"""hj212parser 单元测试"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from hj212parser import HJ212Parser, build_message  # noqa: E402


class TestHJ212Parser(unittest.TestCase):
    def setUp(self):
        self.parser = HJ212Parser()
        self.segment = (
            "ST=32;CN=2011;PW=123456;MN=88888880000001;Flag=3;"
            "CP=&&DataTime=20240101120000;w01018-Rtd=7.5;w01018-Flag=N&&"
        )
        self.message = build_message(self.segment)

    # ---------- is_valid_message ----------
    def test_valid_message(self):
        self.assertTrue(self.parser.is_valid_message(self.message))

    def test_valid_message_without_crlf(self):
        self.assertTrue(self.parser.is_valid_message(self.message.rstrip("\r\n")))

    def test_invalid_prefix(self):
        bad = "$$" + self.message[2:]
        self.assertFalse(self.parser.is_valid_message(bad))

    def test_invalid_length(self):
        bad = "##0001" + self.message[6:]
        self.assertFalse(self.parser.is_valid_message(bad))

    def test_invalid_crc(self):
        bad = self.message[:-6] + "0000\r\n"
        self.assertFalse(self.parser.is_valid_message(bad))

    def test_empty_string(self):
        self.assertFalse(self.parser.is_valid_message(""))

    # ---------- validate_crc ----------
    def test_crc_correct(self):
        self.assertTrue(self.parser.validate_crc(self.message))

    def test_crc_wrong(self):
        bad = self.message.replace(self.message[-6:-2], "ZZZZ", 1) if False else \
            self.message[:-6] + "AAAA\r\n"
        self.assertFalse(self.parser.validate_crc(bad))

    # ---------- parse_data_segment ----------
    def test_parse_data_segment(self):
        data = self.parser.parse_data_segment(self.message)
        self.assertEqual(data["ST"], "32")
        self.assertEqual(data["CN"], "2011")
        self.assertEqual(data["PW"], "123456")
        self.assertEqual(data["MN"], "88888880000001")
        self.assertEqual(data["Flag"], "3")
        self.assertIsInstance(data["CP"], dict)
        self.assertEqual(data["CP"]["w01018-Rtd"], "7.5")

    def test_parse_data_segment_invalid(self):
        with self.assertRaises(ValueError):
            self.parser.parse_data_segment("bad message")

    # ---------- extract_monitoring_data ----------
    def test_extract_monitoring_data(self):
        data = self.parser.extract_monitoring_data(self.message)
        self.assertEqual(data["DataTime"], "20240101120000")
        self.assertEqual(data["w01018-Rtd"], "7.5")
        self.assertEqual(data["w01018-Flag"], "N")

    def test_extract_no_cp(self):
        seg = "ST=32;CN=2011;PW=123456;MN=88888880000001;Flag=3"
        msg = build_message(seg)
        self.assertEqual(self.parser.extract_monitoring_data(msg), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
