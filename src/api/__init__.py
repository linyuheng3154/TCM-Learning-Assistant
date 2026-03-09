"""
API模块 - API Endpoints Package

本包包含所有API端点定义。

模块说明：
- formulas: 方剂相关API接口

AI协作说明：
- 每个模块对应一组相关的API端点
- 使用 FastAPI Router 进行路由组织
- 所有接口都有详细的文档字符串
"""

from src.api import formulas

__all__ = ["formulas"]
