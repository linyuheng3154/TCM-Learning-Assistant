"""
测试配置和共享工具
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))