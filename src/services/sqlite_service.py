"""
SQLite 方剂服务 - SQLite Formula Service

基于 SQLite 数据库的方剂服务实现。

AI协作说明：
- 提供与 JSON 服务相同的接口
- 支持更高效的查询和统计
- 与 JSON 服务可以无缝切换
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from contextlib import contextmanager

from src.models.formula import (
    FormulaModel,
    FormulaBriefModel,
    FormulaSearchResult,
    HerbComposition,
)
from src.database import (
    get_session,
    FormulaDB,
    HerbCompositionDB,
    FormulaAliasDB,
    ClinicalCaseDB,
)


class SQLiteFormulaService:
    """
    基于 SQLite 的方剂服务
    
    提供与 FormulaService 相同的接口，使用 SQLite 作为数据源。
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化 SQLite 方剂服务
        
        Args:
            db_path: SQLite 数据库路径
        """
        if db_path is None:
            current_dir = Path(__file__).parent.parent.parent
            db_path = current_dir / "data" / "tcm.db"
        
        self.db_path = str(db_path)
        self._metadata_cache: Optional[Dict[str, Any]] = None
    
    @contextmanager
    def _get_session(self):
        """获取数据库会话的上下文管理器"""
        session = get_session()
        try:
            yield session
        finally:
            session.close()
    
    def _db_to_model(self, db_formula: FormulaDB) -> FormulaModel:
        """将数据库模型转换为 Pydantic 模型"""
        compositions = [
            HerbComposition(
                herb=c.herb_name,
                dosage=c.dosage or "",
                role=c.role,
                note=c.note,
            )
            for c in db_formula.compositions
        ]
        
        return FormulaModel(
            id=db_formula.id,
            name=db_formula.name,
            pinyin=db_formula.pinyin or "",
            composition=compositions,
            efficacy=db_formula.efficacy or "",
            indications=db_formula.indications or "",
            contraindications=db_formula.contraindications,
            usage=db_formula.usage,
            source=db_formula.source,
            category=db_formula.category,
        )
    
    def _load_metadata(self) -> Dict[str, Any]:
        """加载元数据"""
        if self._metadata_cache is not None:
            return self._metadata_cache
        
        from src.database import DataMetadataDB
        
        with self._get_session() as session:
            metadata_records = session.query(DataMetadataDB).all()
            self._metadata_cache = {r.key: r.value for r in metadata_records}
        
        return self._metadata_cache
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """获取数据元信息"""
        return self._load_metadata()
    
    def get_all_formulas(self) -> List[FormulaBriefModel]:
        """获取所有方剂的简要信息列表"""
        with self._get_session() as session:
            formulas = session.query(FormulaDB).order_by(FormulaDB.id).all()
            
            return [
                FormulaBriefModel(
                    id=f.id,
                    name=f.name,
                    efficacy=f.efficacy or "",
                    category=f.category,
                )
                for f in formulas
            ]
    
    def get_formula_by_id(self, formula_id: str) -> Optional[FormulaModel]:
        """根据 ID 获取方剂完整信息"""
        with self._get_session() as session:
            db_formula = session.query(FormulaDB).filter_by(id=formula_id).first()
            
            if db_formula is None:
                return None
            
            return self._db_to_model(db_formula)
    
    def get_formula_by_name(self, name: str) -> Optional[FormulaModel]:
        """根据名称获取方剂信息"""
        with self._get_session() as session:
            # 精确匹配
            db_formula = session.query(FormulaDB).filter_by(name=name).first()
            
            if db_formula is None:
                # 模糊匹配
                db_formula = session.query(FormulaDB).filter(
                    FormulaDB.name.contains(name)
                ).first()
            
            if db_formula is None:
                return None
            
            return self._db_to_model(db_formula)
    
    def search_formulas(
        self,
        keyword: str,
        limit: int = 10,
        fields: Optional[List[str]] = None
    ) -> List[FormulaSearchResult]:
        """搜索方剂"""
        if fields is None:
            fields = ["name", "efficacy", "indications", "pinyin", "category"]
        
        with self._get_session() as session:
            keyword_lower = keyword.lower()
            results = []
            
            # 构建查询
            formulas = session.query(FormulaDB).all()
            
            for formula in formulas:
                matched_fields = []
                score = 0.0
                
                for field in fields:
                    value = getattr(formula, field, None)
                    if value is None:
                        continue
                    
                    value_lower = str(value).lower()
                    
                    if keyword_lower in value_lower:
                        matched_fields.append(field)
                        
                        if field == "name":
                            if keyword_lower == value_lower:
                                score += 1.0
                            else:
                                score += 0.8
                        elif field == "pinyin":
                            score += 0.7
                        elif field == "efficacy":
                            score += 0.5
                        elif field == "indications":
                            score += 0.4
                        else:
                            score += 0.3
                
                if matched_fields:
                    score = min(score, 1.0)
                    
                    results.append(FormulaSearchResult(
                        formula=FormulaBriefModel(
                            id=formula.id,
                            name=formula.name,
                            efficacy=formula.efficacy or "",
                            category=formula.category,
                        ),
                        score=score,
                        matched_fields=matched_fields,
                    ))
            
            # 排序并返回
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:limit]
    
    def get_formulas_by_category(self, category: str) -> List[FormulaBriefModel]:
        """根据分类获取方剂列表"""
        with self._get_session() as session:
            formulas = session.query(FormulaDB).filter(
                FormulaDB.category.contains(category)
            ).all()
            
            return [
                FormulaBriefModel(
                    id=f.id,
                    name=f.name,
                    efficacy=f.efficacy or "",
                    category=f.category,
                )
                for f in formulas
            ]
    
    def get_formulas_containing_herb(self, herb_name: str) -> List[FormulaBriefModel]:
        """获取包含指定药材的方剂"""
        with self._get_session() as session:
            compositions = session.query(HerbCompositionDB).filter(
                HerbCompositionDB.herb_name.contains(herb_name)
            ).all()
            
            seen_ids = set()
            results = []
            
            for comp in compositions:
                if comp.formula_id in seen_ids:
                    continue
                seen_ids.add(comp.formula_id)
                
                formula = session.query(FormulaDB).filter_by(id=comp.formula_id).first()
                if formula:
                    results.append(FormulaBriefModel(
                        id=formula.id,
                        name=formula.name,
                        efficacy=formula.efficacy or "",
                        category=formula.category,
                    ))
            
            return results
    
    def get_herb_usage_stats(self, herb_name: str) -> Dict[str, Any]:
        """
        获取药材使用统计
        
        Args:
            herb_name: 药材名称
        
        Returns:
            统计信息字典
        """
        with self._get_session() as session:
            compositions = session.query(HerbCompositionDB).filter(
                HerbCompositionDB.herb_name.contains(herb_name)
            ).all()
            
            formula_count = len(set(c.formula_id for c in compositions))
            
            # 统计配伍角色
            role_stats = {}
            for comp in compositions:
                role = comp.role or "未分类"
                role_stats[role] = role_stats.get(role, 0) + 1
            
            return {
                "herb_name": herb_name,
                "formula_count": formula_count,
                "role_distribution": role_stats,
            }


# 如果需要使用 SQLite 服务，可以创建实例
# sqlite_formula_service = SQLiteFormulaService()
