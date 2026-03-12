"""
中医辨证推荐服务 - TCM Diagnosis Service

本模块提供基于症状的中医辨证推荐功能，包括：
1. 症状解析与标准化
2. 证型识别与匹配
3. 方剂智能推荐
4. 推荐结果解释

AI协作说明：
- 核心算法基于症状关键词匹配与评分
- 支持调用外部 AI API 进行深度分析（可选）
- 返回结构化推荐结果，便于前端展示

免责声明：
本功能仅供学习和参考，不能替代专业医生的诊断。
如有健康问题，请咨询专业中医师。
"""

import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass

from src.models.formula import FormulaBriefModel
from src.services.formula_service import formula_service


@dataclass
class SyndromeMatch:
    """证型匹配结果"""
    syndrome_id: str
    syndrome_name: str
    description: str
    matched_keywords: List[str]
    score: float  # 0.0 - 1.0


@dataclass
class DiagnosisResult:
    """辨证推荐结果"""
    symptoms: List[str]
    matched_syndromes: List[SyndromeMatch]
    recommended_formulas: List[Dict[str, Any]]
    confidence: float  # 整体置信度 0.0 - 1.0
    disclaimer: str


class DiagnosisService:
    """
    中医辨证推荐服务
    
    基于症状关键词匹配，识别证型并推荐相应方剂。
    
    使用示例:
        service = DiagnosisService()
        result = service.diagnose(["发热", "恶寒", "无汗", "头痛"])
        print(result.recommended_formulas)
    """
    
    # 免责声明
    DISCLAIMER = "本结果仅供学习参考，不能替代专业医生诊断。如有健康问题，请咨询专业中医师。"
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化辨证服务
        
        Args:
            data_dir: 数据文件目录路径
        """
        if data_dir is None:
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
        
        self.data_dir = Path(data_dir)
        self._syndromes_cache: Optional[List[Dict]] = None
    
    def _load_syndromes(self) -> None:
        """加载证型数据"""
        if self._syndromes_cache is not None:
            return
        
        file_path = self.data_dir / "syndrome_formulas.json"
        
        if not file_path.exists():
            self._syndromes_cache = []
            return
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._syndromes_cache = data.get("syndromes", [])
    
    def _normalize_symptom(self, symptom: str) -> str:
        """
        标准化症状描述
        
        Args:
            symptom: 原始症状描述
        
        Returns:
            标准化后的症状
        """
        # 去除空格和标点
        symptom = symptom.strip()
        
        # 常见症状同义词映射
        symptom_aliases = {
            "怕冷": "恶寒",
            "怕风": "恶风",
            "不出汗": "无汗",
            "拉肚子": "泄泻",
            "拉稀": "泄泻",
            "大便干": "便秘",
            "大便干结": "便秘",
            "睡不着": "失眠",
            "睡不着觉": "失眠",
            "没力气": "乏力",
            "没精神": "乏力",
            "身体乏力": "乏力",
            "浑身无力": "乏力",
            "口干": "咽干",
            "嗓子干": "咽干",
            "嗓子疼": "咽喉肿痛",
            "喉咙痛": "咽喉肿痛",
            "头疼": "头痛",
            "头晕眼花": "头晕",
            "腰酸": "腰膝酸软",
            "腰痛": "腰痛",
            "肚子胀": "腹胀",
            "肚子疼": "腹痛",
            "恶心呕吐": "呕吐",
            "想吐": "呕吐",
        }
        
        return symptom_aliases.get(symptom, symptom)
    
    def _calculate_match_score(
        self, 
        symptoms: List[str], 
        syndrome_keywords: List[str]
    ) -> tuple[float, List[str]]:
        """
        计算症状与证型的匹配度
        
        Args:
            symptoms: 用户症状列表
            syndrome_keywords: 证型关键词列表
        
        Returns:
            (匹配分数, 匹配的关键词列表)
        """
        normalized_symptoms = [self._normalize_symptom(s) for s in symptoms]
        matched_keywords = []
        
        for keyword in syndrome_keywords:
            # 精确匹配
            if keyword in normalized_symptoms:
                matched_keywords.append(keyword)
                continue
            
            # 模糊匹配（关键词包含在症状中）
            for symptom in normalized_symptoms:
                if keyword in symptom or symptom in keyword:
                    matched_keywords.append(keyword)
                    break
        
        if not syndrome_keywords:
            return 0.0, []
        
        # 计算匹配率
        match_rate = len(matched_keywords) / len(syndrome_keywords)
        
        # 额外加成：如果匹配数量超过一定阈值
        if len(matched_keywords) >= 3:
            match_rate = min(1.0, match_rate * 1.2)
        
        return match_rate, matched_keywords
    
    def diagnose(
        self,
        symptoms: List[str],
        top_k: int = 3,
        min_score: float = 0.1
    ) -> DiagnosisResult:
        """
        根据症状进行辨证推荐
        
        Args:
            symptoms: 症状列表
            top_k: 返回前 K 个匹配结果
            min_score: 最低匹配分数阈值
        
        Returns:
            DiagnosisResult: 辨证推荐结果
        """
        self._load_syndromes()
        
        if not symptoms:
            return DiagnosisResult(
                symptoms=[],
                matched_syndromes=[],
                recommended_formulas=[],
                confidence=0.0,
                disclaimer=self.DISCLAIMER
            )
        
        # 计算每个证型的匹配度
        matches: List[SyndromeMatch] = []
        
        for syndrome in self._syndromes_cache:
            score, matched_kw = self._calculate_match_score(
                symptoms, 
                syndrome.get("keywords", [])
            )
            
            if score >= min_score:
                matches.append(SyndromeMatch(
                    syndrome_id=syndrome["id"],
                    syndrome_name=syndrome["name"],
                    description=syndrome["description"],
                    matched_keywords=matched_kw,
                    score=score
                ))
        
        # 按分数排序，取前 K 个
        matches.sort(key=lambda x: x.score, reverse=True)
        top_matches = matches[:top_k]
        
        # 获取推荐的方剂
        recommended_formulas = []
        seen_formula_ids = set()
        
        for match in top_matches:
            syndrome_data = next(
                (s for s in self._syndromes_cache if s["id"] == match.syndrome_id),
                None
            )
            
            if not syndrome_data:
                continue
            
            for formula_id in syndrome_data.get("formulas", []):
                if formula_id in seen_formula_ids:
                    continue
                
                formula = formula_service.get_formula_by_id(formula_id)
                if formula:
                    seen_formula_ids.add(formula_id)
                    recommended_formulas.append({
                        "id": formula.id,
                        "name": formula.name,
                        "efficacy": formula.efficacy,
                        "indications": formula.indications,
                        "matched_syndrome": match.syndrome_name,
                        "match_score": match.score,
                        "matched_keywords": match.matched_keywords,
                        "source": formula.source
                    })
        
        # 计算整体置信度
        confidence = sum(m.score for m in top_matches) / len(top_matches) if top_matches else 0.0
        
        return DiagnosisResult(
            symptoms=symptoms,
            matched_syndromes=top_matches,
            recommended_formulas=recommended_formulas,
            confidence=round(confidence, 2),
            disclaimer=self.DISCLAIMER
        )
    
    def get_syndrome_by_id(self, syndrome_id: str) -> Optional[Dict]:
        """
        根据ID获取证型信息
        
        Args:
            syndrome_id: 证型ID
        
        Returns:
            证型信息字典
        """
        self._load_syndromes()
        
        for syndrome in self._syndromes_cache:
            if syndrome["id"] == syndrome_id:
                return syndrome
        
        return None
    
    def get_all_syndromes(self) -> List[Dict]:
        """获取所有证型列表"""
        self._load_syndromes()
        return self._syndromes_cache or []


# 创建全局服务实例
diagnosis_service = DiagnosisService()
