"""
配伍禁忌检查服务 - Herb Compatibility Check Service

检查中药配伍禁忌，包括：
1. 十八反 - 剧烈毒性反应
2. 十九畏 - 药效相互抑制
3. 妊娠禁忌 - 孕妇禁用/慎用药物

数据来源：《本草经集注》《本草纲目》《神农本草经》
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class ContraindicationWarning(BaseModel):
    """配伍禁忌警告"""
    type: str = Field(..., description="禁忌类型：shiba_fan(十八反)/shijiu_wei(十九畏)/pregnancy(妊娠禁忌)")
    severity: str = Field(..., description="严重程度：high/medium")
    herbs: List[str] = Field(..., description="涉及的药材")
    description: str = Field(..., description="禁忌说明")
    source: str = Field(default="", description="出处")


class CompatibilityCheckResult(BaseModel):
    """配伍检查结果"""
    safe: bool = Field(..., description="是否安全")
    warnings: List[ContraindicationWarning] = Field(default_factory=list, description="警告列表")
    summary: str = Field(default="", description="检查摘要")


class HerbCompatibilityService:
    """
    配伍禁忌检查服务
    
    使用示例:
        service = HerbCompatibilityService()
        result = service.check_herbs(["甘草", "大戟", "芫花"])
        # result.safe = False (甘草反大戟、芫花)
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """初始化服务，加载配伍禁忌数据"""
        if data_dir is None:
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
        
        self.data_dir = Path(data_dir)
        self._data: Optional[Dict[str, Any]] = None
        
        # 构建快速查询索引
        self._shiba_fan_index: Dict[str, List[str]] = {}  # {药材: [禁忌药材列表]}
        self._shijiu_wei_index: Dict[str, str] = {}  # {药材: 相畏药材}
        self._pregnancy_index: Dict[str, Dict[str, Any]] = {}  # {药材: 禁忌级别信息}
    
    def _load_data(self) -> None:
        """加载配伍禁忌数据"""
        if self._data is not None:
            return
        
        file_path = self.data_dir / "herb_contraindications.json"
        if not file_path.exists():
            raise FileNotFoundError(f"配伍禁忌数据文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        
        self._build_indexes()
    
    def _build_indexes(self) -> None:
        """构建快速查询索引"""
        # 构建十八反索引
        shiba_fan = self._data.get("shiba_fan", {})
        for rule in shiba_fan.get("rules", []):
            herbs = rule.get("herbs", [])
            incompatible = rule.get("incompatible_with", [])
            for herb in herbs:
                if herb not in self._shiba_fan_index:
                    self._shiba_fan_index[herb] = []
                self._shiba_fan_index[herb].extend(incompatible)
            # 反向索引
            for inc in incompatible:
                if inc not in self._shiba_fan_index:
                    self._shiba_fan_index[inc] = []
                self._shiba_fan_index[inc].extend(herbs)
        
        # 构建十九畏索引
        shijiu_wei = self._data.get("shijiu_wei", {})
        for rule in shijiu_wei.get("rules", []):
            herb1 = rule.get("herb1", "")
            herb2 = rule.get("herb2", "")
            self._shijiu_wei_index[herb1] = herb2
            self._shijiu_wei_index[herb2] = herb1
        
        # 构建妊娠禁忌索引
        pregnancy = self._data.get("pregnancy_contraindications", {})
        for category in pregnancy.get("categories", []):
            level = category.get("level", "")
            severity = category.get("severity", "medium")
            description = category.get("description", "")
            for herb in category.get("herbs", []):
                self._pregnancy_index[herb] = {
                    "level": level,
                    "severity": severity,
                    "description": description
                }
    
    def check_herbs(self, herbs: List[str], is_pregnant: bool = False) -> CompatibilityCheckResult:
        """
        检查药材配伍禁忌
        
        Args:
            herbs: 药材列表
            is_pregnant: 是否孕妇（检查妊娠禁忌）
        
        Returns:
            CompatibilityCheckResult: 检查结果
        """
        self._load_data()
        
        warnings = []
        herbs_set = set(herbs)
        
        # 检查十八反
        for herb in herbs:
            if herb in self._shiba_fan_index:
                incompatible = set(self._shiba_fan_index[herb]) & herbs_set
                if incompatible:
                    warnings.append(ContraindicationWarning(
                        type="shiba_fan",
                        severity="high",
                        herbs=[herb] + list(incompatible),
                        description=f"'{herb}' 与 {', '.join(incompatible)} 属于十八反禁忌，同用可能产生剧烈毒性反应",
                        source="《本草经集注》"
                    ))
        
        # 检查十九畏
        checked_pairs = set()
        for herb in herbs:
            if herb in self._shijiu_wei_index:
                conflict = self._shijiu_wei_index[herb]
                if conflict in herbs_set:
                    pair = tuple(sorted([herb, conflict]))
                    if pair not in checked_pairs:
                        checked_pairs.add(pair)
                        warnings.append(ContraindicationWarning(
                            type="shijiu_wei",
                            severity="medium",
                            herbs=[herb, conflict],
                            description=f"'{herb}' 与 '{conflict}' 属于十九畏，同用可能相互抑制药效",
                            source="《本草纲目》引《药性赋》"
                        ))
        
        # 检查妊娠禁忌
        if is_pregnant:
            for herb in herbs:
                if herb in self._pregnancy_index:
                    info = self._pregnancy_index[herb]
                    severity = "high" if info["severity"] == "高" or info["severity"] == "中高" else "medium"
                    warnings.append(ContraindicationWarning(
                        type="pregnancy",
                        severity=severity,
                        herbs=[herb],
                        description=f"'{herb}' 为妊娠{info['level']}药物：{info['description']}",
                        source="《神农本草经》《本草纲目》"
                    ))
        
        # 去重警告（基于类型和药材组合）
        unique_warnings = []
        seen = set()
        for w in warnings:
            key = (w.type, tuple(sorted(w.herbs)))
            if key not in seen:
                seen.add(key)
                unique_warnings.append(w)
        
        # 生成摘要
        if not unique_warnings:
            summary = "配伍检查通过，未发现禁忌"
        else:
            high_count = sum(1 for w in unique_warnings if w.severity == "high")
            medium_count = len(unique_warnings) - high_count
            parts = []
            if high_count > 0:
                parts.append(f"{high_count}个高风险禁忌")
            if medium_count > 0:
                parts.append(f"{medium_count}个中等风险禁忌")
            summary = f"发现{'、'.join(parts)}，请谨慎配伍"
        
        return CompatibilityCheckResult(
            safe=len(unique_warnings) == 0,
            warnings=unique_warnings,
            summary=summary
        )
    
    def check_formula(self, formula_id: str, is_pregnant: bool = False) -> CompatibilityCheckResult:
        """
        检查方剂配伍禁忌
        
        Args:
            formula_id: 方剂ID
            is_pregnant: 是否孕妇
        
        Returns:
            CompatibilityCheckResult: 检查结果
        """
        from src.services.formula_service import formula_service
        
        formula = formula_service.get_formula_by_id(formula_id)
        if formula is None:
            raise ValueError(f"方剂不存在: {formula_id}")
        
        herbs = [comp.herb for comp in formula.composition]
        result = self.check_herbs(herbs, is_pregnant)
        
        return result
    
    def get_shiba_fan_verse(self) -> str:
        """获取十八反歌诀"""
        self._load_data()
        return self._data.get("shiba_fan", {}).get("verse", "")
    
    def get_shijiu_wei_verse(self) -> str:
        """获取十九畏歌诀"""
        self._load_data()
        return self._data.get("shijiu_wei", {}).get("verse", "")


# 全局服务实例
herb_compatibility_service = HerbCompatibilityService()
