#!/usr/bin/env python3
"""
云瞻威胁情报查询技能测试文件
"""

import unittest
import os
import sys

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from hs_ti_plugin import YunzhanThreatIntel

class TestYunzhanThreatIntel(unittest.TestCase):
    """云瞻威胁情报查询测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        if os.path.exists(self.config_path):
            self.yz = YunzhanThreatIntel()
        else:
            self.yz = YunzhanThreatIntel()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.yz)
    
    def test_query_ioc(self):
        """测试IOC查询（需要有效的API密钥）"""
        # 这里只测试方法存在性，实际查询需要有效密钥
        self.assertTrue(hasattr(self.yz, 'query_ioc'))
    
    def test_batch_query(self):
        """测试批量查询（需要有效的API密钥）"""
        # 这里只测试方法存在性，实际查询需要有效密钥
        self.assertTrue(hasattr(self.yz, 'batch_query'))

if __name__ == '__main__':
    unittest.main()