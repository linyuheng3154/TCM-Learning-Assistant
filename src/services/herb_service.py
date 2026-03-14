"""
药材服务层 - Herb Service Layer

本模块提供药材相关的业务逻辑，包括：
1. 药材数据的加载和缓存
2. 药材的查询和搜索功能
3. 药材使用统计（与方剂的关联分析）

AI协作说明：
- 所有方法都有详细的文档字符串，说明输入输出格式
- 统计功能基于方剂数据，分析药材的使用频率和配伍规律
- 返回的数据结构使用 Pydantic 模型，便于类型检查和文档生成
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from collections import Counter

from src.models.herb import (
    HerbModel,
    HerbBriefModel,
    HerbSearchResult
)


class HerbService:
    """
    药材服务类
    
    提供药材数据的查询、搜索和统计分析功能。
    
    使用示例:
        service = HerbService()
        
        # 获取所有药材列表
        herbs = service.get_all_herbs()
        
        # 根据ID查询药材
        herb = service.get_herb_by_id("h003")
        
        # 搜索药材
        results = service.search_herbs("人参")
        
        # 获取药材使用统计
        stats = service.get_herb_stats("桂枝")
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化药材服务
        
        Args:
            data_dir: 数据文件目录路径，默认为项目根目录下的 data 文件夹
        """
        if data_dir is None:
            # 获取项目根目录
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
        
        self.data_dir = Path(data_dir)
        self._herbs_cache: Optional[Dict[str, HerbModel]] = None
        self._herbs_by_name: Optional[Dict[str, HerbModel]] = None
        self._metadata: Optional[Dict[str, Any]] = None
        self._formulas_cache: Optional[List[Dict]] = None
    
    def _load_herbs_data(self) -> None:
        """
        加载药材数据文件
        
        数据格式说明：
        - 文件位置: data/herbs.json
        - 包含 _metadata 和 herbs 两个主要字段
        - _metadata 包含数据来源、更新时间等元信息
        - herbs 是药材列表
        """
        if self._herbs_cache is not None:
            return
        
        file_path = self.data_dir / "herbs.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"药材数据文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._metadata = data.get("_metadata", {})
        
        # 将药材列表转换为字典，以 ID 为键
        self._herbs_cache = {}
        self._herbs_by_name = {}
        
        for item in data.get("herbs", []):
            herb = HerbModel(**item)
            self._herbs_cache[herb.id] = herb
            # 建立名称索引（包括别名）
            self._herbs_by_name[herb.name] = herb
            for alias in herb.alias:
                self._herbs_by_name[alias] = herb
    
    def _load_formulas_data(self) -> None:
        """
        加载方剂数据用于统计分析
        """
        if self._formulas_cache is not None:
            return
        
        file_path = self.data_dir / "formulas.json"
        
        if not file_path.exists():
            self._formulas_cache = []
            return
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._formulas_cache = data.get("formulas", [])
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """获取数据元信息"""
        self._load_herbs_data()
        return self._metadata or {}
    
    def get_all_herbs(self) -> List[HerbBriefModel]:
        """
        获取所有药材简要信息列表
        
        Returns:
            List[HerbBriefModel]: 药材简要信息列表
        """
        self._load_herbs_data()
        
        herbs = []
        for herb in self._herbs_cache.values():
            herbs.append(HerbBriefModel(
                id=herb.id,
                name=herb.name,
                nature=herb.nature,
                efficacy=herb.efficacy[:50] + "..." if len(herb.efficacy) > 50 else herb.efficacy
            ))
        
        return herbs
    
    def get_herb_by_id(self, herb_id: str) -> Optional[HerbModel]:
        """
        根据ID获取药材详情
        
        Args:
            herb_id: 药材ID，格式为 "h" + 三位数字，如 "h003"
        
        Returns:
            HerbModel: 药材完整信息，不存在则返回 None
        """
        self._load_herbs_data()
        return self._herbs_cache.get(herb_id)
    
    def get_herb_by_name(self, name: str) -> Optional[HerbModel]:
        """
        根据名称获取药材详情（支持别名查询）
        
        Args:
            name: 药材名称或别名
        
        Returns:
            HerbModel: 药材完整信息，不存在则返回 None
        """
        self._load_herbs_data()
        return self._herbs_by_name.get(name)
    
    def search_herbs(self, keyword: str, limit: int = 10) -> List[HerbSearchResult]:
        """
        搜索药材
        
        搜索范围包括：名称、拼音、别名、功效、主治
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
        
        Returns:
            List[HerbSearchResult]: 搜索结果列表，按匹配度排序
        """
        self._load_herbs_data()
        
        results = []
        keyword_lower = keyword.lower()
        
        for herb in self._herbs_cache.values():
            score = 0.0
            matched_fields = []
            
            # 名称匹配（权重最高）
            if keyword_lower in herb.name.lower():
                score = 1.0
                matched_fields.append("name")
            # 拼音匹配
            elif herb.pinyin and keyword_lower in herb.pinyin.lower():
                score = 0.9
                matched_fields.append("pinyin")
            # 别名匹配
            elif any(keyword_lower in alias.lower() for alias in herb.alias):
                score = 0.85
                matched_fields.append("alias")
            # 功效匹配
            elif keyword_lower in herb.efficacy.lower():
                score = 0.6
                matched_fields.append("efficacy")
            # 主治匹配
            elif keyword_lower in herb.indications.lower():
                score = 0.5
                matched_fields.append("indications")
            
            if score > 0:
                results.append(HerbSearchResult(
                    herb=HerbBriefModel(
                        id=herb.id,
                        name=herb.name,
                        nature=herb.nature,
                        efficacy=herb.efficacy[:50] + "..." if len(herb.efficacy) > 50 else herb.efficacy
                    ),
                    score=score,
                    matched_fields=matched_fields
                ))
        
        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
    
    def get_herb_stats(self, herb_name: str) -> Dict[str, Any]:
        """
        获取药材使用统计
        
        分析该药材在方剂中的使用情况，包括：
        - 使用频次
        - 所在方剂列表
        - 配伍角色分布（君/臣/佐/使）
        
        Args:
            herb_name: 药材名称
        
        Returns:
            Dict: 统计信息
        """
        self._load_herbs_data()
        self._load_formulas_data()
        
        # 查找药材
        herb = self.get_herb_by_name(herb_name)
        if not herb:
            return {"error": f"药材 '{herb_name}' 不存在"}
        
        # 统计使用情况
        formulas_using_herb = []
        role_counter = Counter()
        
        for formula in self._formulas_cache:
            composition = formula.get("composition", [])
            for comp in composition:
                comp_herb = comp.get("herb", "")
                if herb_name == comp_herb or herb_name in comp_herb:
                    formulas_using_herb.append({
                        "id": formula.get("id"),
                        "name": formula.get("name"),
                        "dosage": comp.get("dosage", ""),
                        "role": comp.get("role", "")
                    })
                    role = comp.get("role", "未分类")
                    if role:
                        role_counter[role] += 1
                    break
        
        return {
            "herb": {
                "id": herb.id,
                "name": herb.name,
                "nature": herb.nature,
                "efficacy": herb.efficacy
            },
            "usage_count": len(formulas_using_herb),
            "formulas": formulas_using_herb[:20],  # 最多返回20个方剂
            "role_distribution": dict(role_counter),
            "total_formulas_analyzed": len(self._formulas_cache)
        }
    
    def get_herbs_by_nature(self, nature: str) -> List[HerbBriefModel]:
        """
        按性味获取药材列表
        
        Args:
            nature: 性味关键词，如 "温"、"寒"、"平"
        
        Returns:
            List[HerbBriefModel]: 符合条件的药材列表
        """
        self._load_herbs_data()
        
        herbs = []
        for herb in self._herbs_cache.values():
            if nature in herb.nature:
                herbs.append(HerbBriefModel(
                    id=herb.id,
                    name=herb.name,
                    nature=herb.nature,
                    efficacy=herb.efficacy[:50] + "..." if len(herb.efficacy) > 50 else herb.efficacy
                ))
        
        return herbs
    
    def get_herbs_by_meridian(self, meridian: str) -> List[HerbBriefModel]:
        """
        按归经获取药材列表
        
        Args:
            meridian: 归经关键词，如 "肺"、"脾"、"肾"
        
        Returns:
            List[HerbBriefModel]: 符合条件的药材列表
        """
        self._load_herbs_data()
        
        herbs = []
        for herb in self._herbs_cache.values():
            if meridian in herb.meridian:
                herbs.append(HerbBriefModel(
                    id=herb.id,
                    name=herb.name,
                    nature=herb.nature,
                    efficacy=herb.efficacy[:50] + "..." if len(herb.efficacy) > 50 else herb.efficacy
                ))
        
        return herbs


# 全局服务实例
herb_service = HerbService()
