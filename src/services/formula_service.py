"""
方剂服务层 - Formula Service Layer

本模块提供方剂相关的业务逻辑，包括：
1. 方剂数据的加载和缓存
2. 方剂的查询和搜索功能
3. 基于症状的方剂推荐

AI协作说明：
- 所有方法都有详细的文档字符串，说明输入输出格式
- 搜索算法使用简单的字符串匹配，后续可升级为语义搜索
- 返回的数据结构使用 Pydantic 模型，便于类型检查和文档生成

性能说明：
- 数据首次加载后会缓存在内存中，避免重复读取文件
- 搜索使用线性扫描，适用于当前数据量（<1000条）
- 如需支持大规模数据，建议改用向量数据库（如 Milvus、Pinecone）
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from src.models.formula import (
    FormulaModel,
    FormulaBriefModel,
    FormulaSearchResult,
    HerbComposition,
    FormulaCompareResult,
    HerbCompareResult,
    FormulaVariation,
    FormulaVariationResult,
    HerbVariation
)


class FormulaService:
    """
    方剂服务类
    
    提供方剂数据的查询、搜索和推荐功能。
    
    使用示例:
        service = FormulaService()
        
        # 获取所有方剂列表
        formulas = service.get_all_formulas()
        
        # 根据ID查询方剂
        formula = service.get_formula_by_id("f002")
        
        # 搜索方剂
        results = service.search_formulas("感冒")
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化方剂服务
        
        Args:
            data_dir: 数据文件目录路径，默认为项目根目录下的 data 文件夹
        """
        if data_dir is None:
            # 获取项目根目录
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
        
        self.data_dir = Path(data_dir)
        self._formulas_cache: Optional[Dict[str, FormulaModel]] = None
        self._variations_cache: Optional[List[FormulaVariation]] = None
        self._metadata: Optional[Dict[str, Any]] = None
    
    def _load_data(self) -> None:
        """
        加载方剂数据文件
        
        数据格式说明：
        - 文件位置: data/formulas.json
        - 包含 _metadata 和 formulas 两个主要字段
        - _metadata 包含数据来源、更新时间等元信息
        - formulas 是方剂列表
        """
        if self._formulas_cache is not None:
            return
        
        file_path = self.data_dir / "formulas.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"方剂数据文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._metadata = data.get("_metadata", {})
        
        # 将方剂列表转换为字典，以 ID 为键
        self._formulas_cache = {}
        for item in data.get("formulas", []):
            formula = FormulaModel(**item)
            self._formulas_cache[formula.id] = formula
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """获取数据元信息"""
        self._load_data()
        return self._metadata or {}
    
    def get_all_formulas(self) -> List[FormulaBriefModel]:
        """
        获取所有方剂的简要信息列表
        
        Returns:
            方剂简要信息列表，按 ID 排序
        
        使用场景:
            - 方剂列表页面展示
            - 下拉选择框数据源
        """
        self._load_data()
        
        return [
            FormulaBriefModel(
                id=f.id,
                name=f.name,
                efficacy=f.efficacy,
                category=f.category
            )
            for f in sorted(self._formulas_cache.values(), key=lambda x: x.id)
        ]
    
    def get_formula_by_id(self, formula_id: str) -> Optional[FormulaModel]:
        """
        根据 ID 获取方剂完整信息
        
        Args:
            formula_id: 方剂ID，格式为 "f" + 三位数字，如 "f002"
        
        Returns:
            方剂完整信息，如不存在返回 None
        
        使用场景:
            - 方剂详情页面
            - API 单条查询
        """
        self._load_data()
        return self._formulas_cache.get(formula_id)
    
    def get_formula_by_name(self, name: str) -> Optional[FormulaModel]:
        """
        根据名称获取方剂信息
        
        Args:
            name: 方剂名称（支持模糊匹配）
        
        Returns:
            第一个匹配的方剂，如不存在返回 None
        """
        self._load_data()
        
        # 先精确匹配
        for formula in self._formulas_cache.values():
            if formula.name == name:
                return formula
        
        # 再模糊匹配
        for formula in self._formulas_cache.values():
            if name in formula.name or formula.name in name:
                return formula
        
        return None
    
    def search_formulas(
        self,
        keyword: str,
        limit: int = 10,
        fields: Optional[List[str]] = None
    ) -> List[FormulaSearchResult]:
        """
        搜索方剂
        
        搜索逻辑：
        1. 在指定字段中查找关键词
        2. 计算匹配度评分（基于匹配字段数量和匹配位置）
        3. 按评分降序排序返回结果
        4. 支持拼音首字母搜索（如 "gzt" 匹配 "桂枝汤"）
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制，默认10条
            fields: 搜索字段列表，默认为 ["name", "efficacy", "indications", "pinyin", "pinyin_initials", "category"]
        
        Returns:
            搜索结果列表，包含匹配度评分
        
        使用示例:
            # 搜索治疗感冒的方剂
            results = service.search_formulas("感冒")
            
            # 仅在方剂名称中搜索
            results = service.search_formulas("桂枝", fields=["name"])
            
            # 拼音首字母搜索
            results = service.search_formulas("gzt")  # 匹配桂枝汤
        """
        self._load_data()
        
        if fields is None:
            fields = ["name", "efficacy", "indications", "pinyin", "pinyin_initials", "category"]
        
        results = []
        keyword_lower = keyword.lower()
        
        for formula in self._formulas_cache.values():
            matched_fields = []
            score = 0.0
            
            # 计算拼音首字母（如果不存在）
            pinyin_initials = getattr(formula, 'pinyin_initials', None)
            if pinyin_initials is None and formula.pinyin:
                pinyin_initials = self._get_pinyin_initials(formula.pinyin)
            
            for field in fields:
                value = getattr(formula, field, None)
                
                # 特殊处理 pinyin_initials 字段
                if field == "pinyin_initials":
                    value = pinyin_initials
                
                if value is None:
                    continue
                
                value_lower = str(value).lower()
                
                if keyword_lower in value_lower:
                    matched_fields.append(field)
                    
                    # 计算评分权重
                    if field == "name":
                        # 名称匹配权重最高
                        if keyword_lower == value_lower:
                            score += 1.0  # 完全匹配
                        else:
                            score += 0.8  # 部分匹配
                    elif field == "pinyin_initials":
                        # 拼音首字母匹配权重高
                        if keyword_lower == value_lower:
                            score += 0.95  # 完全匹配首字母
                        else:
                            score += 0.7
                    elif field == "pinyin":
                        score += 0.7
                    elif field == "efficacy":
                        score += 0.5
                    elif field == "indications":
                        score += 0.4
                    else:
                        score += 0.3
            
            if matched_fields:
                # 归一化评分
                score = min(score, 1.0)
                
                results.append(FormulaSearchResult(
                    formula=FormulaBriefModel(
                        id=formula.id,
                        name=formula.name,
                        efficacy=formula.efficacy,
                        category=formula.category
                    ),
                    score=score,
                    matched_fields=matched_fields
                ))
        
        # 按评分降序排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
    
    def _get_pinyin_initials(self, pinyin: str) -> str:
        """
        从拼音字符串提取首字母
        
        Args:
            pinyin: 拼音字符串，如 "guizhi tang"
        
        Returns:
            首字母字符串，如 "gzt"
        """
        if not pinyin:
            return ""
        
        # 分割拼音单词，取每个单词的首字母
        words = pinyin.lower().split()
        initials = "".join(word[0] for word in words if word)
        return initials
    
    def get_formulas_by_category(self, category: str) -> List[FormulaBriefModel]:
        """
        根据分类获取方剂列表
        
        Args:
            category: 方剂分类，如 "解表剂-辛温解表"
        
        Returns:
            该分类下的方剂列表
        """
        self._load_data()
        
        return [
            FormulaBriefModel(
                id=f.id,
                name=f.name,
                efficacy=f.efficacy,
                category=f.category
            )
            for f in self._formulas_cache.values()
            if f.category and category in f.category
        ]
    
    def get_formulas_containing_herb(self, herb_name: str) -> List[FormulaBriefModel]:
        """
        获取包含指定药材的方剂
        
        Args:
            herb_name: 药材名称
        
        Returns:
            包含该药材的方剂列表
        
        使用场景:
            - 查看某味药材常用于哪些方剂
            - 药材-方剂关联分析
        """
        self._load_data()
        
        results = []
        for formula in self._formulas_cache.values():
            for composition in formula.composition:
                if herb_name in composition.herb:
                    results.append(FormulaBriefModel(
                        id=formula.id,
                        name=formula.name,
                        efficacy=formula.efficacy,
                        category=formula.category
                    ))
                    break
        
        return results
    
    def compare_formulas(self, formula_ids: List[str]) -> FormulaCompareResult:
        """
        对比多方剂信息
        
        分析多首方剂的组成、功效、主治、禁忌等差异。
        
        Args:
            formula_ids: 要对比的方剂ID列表（2-5个）
        
        Returns:
            FormulaCompareResult: 对比结果
        
        Raises:
            ValueError: 方剂ID数量不在2-5范围内
        """
        self._load_data()
        
        if not (2 <= len(formula_ids) <= 5):
            raise ValueError("对比方剂数量需在2-5个之间")
        
        # 获取所有方剂
        formulas = []
        for fid in formula_ids:
            formula = self._formulas_cache.get(fid)
            if formula is None:
                raise ValueError(f"方剂不存在: {fid}")
            formulas.append(formula)
        
        # 收集所有药材
        all_herbs = {}  # {药材名: {方剂ID: (用量, 角色)}}
        formula_herb_sets = {}  # {方剂ID: set(药材名)}
        
        for formula in formulas:
            herb_set = set()
            for comp in formula.composition:
                herb_name = comp.herb
                herb_set.add(herb_name)
                
                if herb_name not in all_herbs:
                    all_herbs[herb_name] = {}
                
                role = getattr(comp, 'role', None) or ''
                all_herbs[herb_name][formula.id] = (comp.dosage, role)
            
            formula_herb_sets[formula.id] = herb_set
        
        # 找出共同药材和各方剂独有药材
        if formula_herb_sets:
            common_herbs = set.intersection(*formula_herb_sets.values())
        else:
            common_herbs = set()
        
        unique_herbs = {}
        for fid in formula_ids:
            other_herbs = set()
            for other_fid, herb_set in formula_herb_sets.items():
                if other_fid != fid:
                    other_herbs.update(herb_set)
            unique_herbs[fid] = list(formula_herb_sets[fid] - other_herbs)
        
        # 构建药材对比结果
        herbs_comparison = []
        for herb_name in sorted(all_herbs.keys()):
            usage_dict = {}
            roles_dict = {}
            for fid in formula_ids:
                if fid in all_herbs[herb_name]:
                    usage_dict[fid], roles_dict[fid] = all_herbs[herb_name][fid]
                else:
                    usage_dict[fid] = "-"
                    roles_dict[fid] = "-"
            
            herbs_comparison.append(HerbCompareResult(
                herb=herb_name,
                usage=usage_dict,
                roles=roles_dict
            ))
        
        # 功效对比
        efficacy_comparison = {f.id: f.efficacy for f in formulas}
        
        # 主治对比
        indications_comparison = {f.id: f.indications for f in formulas}
        
        # 禁忌对比
        contraindications_comparison = {}
        for f in formulas:
            contraindications_comparison[f.id] = f.contraindications or "暂无记载"
        
        # 生成对比摘要
        summary_parts = [f"对比{len(formulas)}首方剂："]
        for f in formulas:
            summary_parts.append(f"- {f.name}：{f.efficacy[:20]}...")
        summary_parts.append(f"\n共同药材：{', '.join(common_herbs) if common_herbs else '无'}")
        
        summary = "\n".join(summary_parts)
        
        # 构建简要信息列表
        brief_formulas = [
            FormulaBriefModel(
                id=f.id,
                name=f.name,
                efficacy=f.efficacy,
                category=f.category
            ) for f in formulas
        ]
        
        return FormulaCompareResult(
            formulas=brief_formulas,
            herbs_comparison=herbs_comparison,
            common_herbs=list(common_herbs),
            unique_herbs=unique_herbs,
            efficacy_comparison=efficacy_comparison,
            indications_comparison=indications_comparison,
            contraindications_comparison=contraindications_comparison,
            summary=summary
        )
    
    def _load_variations(self) -> None:
        """
        加载方剂加减变化数据
        
        数据格式说明：
        - 文件位置: data/formula_variations.json
        - 包含方剂的加减变化信息
        """
        if self._variations_cache is not None:
            return
        
        file_path = self.data_dir / "formula_variations.json"
        
        if not file_path.exists():
            self._variations_cache = []
            return
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._variations_cache = []
        for item in data.get("variations", []):
            variations = [
                HerbVariation(**v) for v in item.get("variations", [])
            ]
            variation = FormulaVariation(
                name=item["name"],
                base_formula_id=item["base_formula_id"],
                variations=variations,
                indication_change=item.get("indication_change", ""),
                source=item.get("source")
            )
            self._variations_cache.append(variation)
    
    def get_formula_variations(self, formula_id: str) -> FormulaVariationResult:
        """
        获取方剂的加减变化
        
        Args:
            formula_id: 方剂ID
        
        Returns:
            FormulaVariationResult: 包含继承来源和衍生方剂
        
        使用场景:
            - 查看方剂的加减变化规律
            - 学习经方演变
        """
        self._load_data()
        self._load_variations()
        
        # 获取基础方剂信息
        formula = self._formulas_cache.get(formula_id)
        if formula is None:
            raise ValueError(f"方剂不存在: {formula_id}")
        
        base_formula = FormulaBriefModel(
            id=formula.id,
            name=formula.name,
            efficacy=formula.efficacy,
            category=formula.category
        )
        
        # 查找继承来源（该方剂是由哪个方剂加减而来）
        inherited_from = []
        for v in self._variations_cache:
            if v.name == formula.name and v.base_formula_id != formula_id:
                # 该方剂是其他方剂的变体
                inherited_from.append(v)
        
        # 查找衍生方剂（该方剂加减变化后的方剂）
        derived_to = [
            v for v in self._variations_cache
            if v.base_formula_id == formula_id and v.variations  # 有实际变化的
        ]
        
        return FormulaVariationResult(
            base_formula=base_formula,
            inherited_from=inherited_from,
            derived_to=derived_to,
            total_variations=len(inherited_from) + len(derived_to)
        )


# 创建全局服务实例（单例模式）
# 使用方法：from src.services.formula_service import formula_service
formula_service = FormulaService()
