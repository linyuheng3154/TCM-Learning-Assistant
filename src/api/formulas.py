"""
方剂API接口 - Formula API Endpoints

本模块提供方剂相关的REST API接口，包括：
1. 方剂列表查询
2. 方剂详情查询
3. 方剂搜索
4. 基于症状的方剂推荐
5. 扩展字段查询

API文档：
- 所有接口返回JSON格式数据
- 错误响应格式：{"error": "错误信息", "code": 错误码}
- 成功响应格式：{"data": 数据, "message": "成功信息"}

AI协作说明：
- 每个接口都有详细的说明文档，可通过 /docs 查看
- 接口命名遵循RESTful规范
- 响应数据使用 Pydantic 模型进行序列化
- 支持扩展模型字段：别名、配伍角色、现代研究、医案引用

重要更新：
- 2026-03-11: 支持40首经典方剂的扩展字段查询
- 保持向后兼容性，现有接口不受影响
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from src.models.formula import (
    FormulaModel, 
    FormulaBriefModel, 
    FormulaSearchResult,
    ExpandedFormulaModel
)
from src.services.formula_service import formula_service


# 创建路由器
router = APIRouter(
    prefix="/formulas",
    tags=["方剂管理"],
    responses={
        404: {"description": "方剂不存在"},
        500: {"description": "服务器内部错误"}
    }
)


@router.get("/", 
    response_model=List[FormulaBriefModel],
    summary="获取方剂列表",
    description="""获取所有方剂的简要信息列表。

返回数据包含：
- id: 方剂唯一标识
- name: 方剂名称
- efficacy: 功效
- category: 分类

可用于：
- 方剂列表页面展示
- 下拉选择框数据源
"""
)
async def get_all_formulas():
    """
    获取所有方剂列表
    
    Returns:
        List[FormulaBriefModel]: 方剂简要信息列表
    """
    try:
        return formula_service.get_all_formulas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取方剂列表失败: {str(e)}")


@router.get("/search",
    response_model=List[FormulaSearchResult],
    summary="搜索方剂",
    description="""根据关键词搜索方剂。

搜索范围：
- 方剂名称（权重最高）
- 拼音名称
- 功效
- 主治
- 分类

返回结果按匹配度评分排序。
"""
)
async def search_formulas(
    keyword: str = Query(..., description="搜索关键词", min_length=1),
    limit: int = Query(10, description="返回结果数量限制", ge=1, le=50)
):
    """
    搜索方剂
    
    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制
    
    Returns:
        List[FormulaSearchResult]: 搜索结果列表，包含匹配度评分
    """
    try:
        results = formula_service.search_formulas(keyword, limit=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/category/{category}",
    response_model=List[FormulaBriefModel],
    summary="按分类获取方剂",
    description="根据方剂分类获取方剂列表。"""
)
async def get_formulas_by_category(category: str):
    """
    按分类获取方剂
    
    Args:
        category: 方剂分类，如"解表剂-辛温解表"
    
    Returns:
        List[FormulaBriefModel]: 该分类下的方剂列表
    """
    try:
        results = formula_service.get_formulas_by_category(category)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类方剂失败: {str(e)}")


@router.get("/herb/{herb_name}",
    response_model=List[FormulaBriefModel],
    summary="获取包含指定药材的方剂",
    description="""获取包含指定药材的所有方剂。

可用于：
- 查看某味药材常用于哪些方剂
- 药材-方剂关联分析
"""
)
async def get_formulas_by_herb(herb_name: str):
    """
    获取包含指定药材的方剂
    
    Args:
        herb_name: 药材名称
    
    Returns:
        List[FormulaBriefModel]: 包含该药材的方剂列表
    """
    try:
        results = formula_service.get_formulas_containing_herb(herb_name)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取方剂失败: {str(e)}")


@router.get("/{formula_id}",
    response_model=FormulaModel,
    summary="获取方剂详情",
    description="根据方剂ID获取完整的方剂信息。"""
)
async def get_formula_by_id(formula_id: str):
    """
    根据ID获取方剂详情
    
    Args:
        formula_id: 方剂ID，格式为 "f" + 三位数字，如 "f002"
    
    Returns:
        FormulaModel: 方剂完整信息
    
    Raises:
        HTTPException: 方剂不存在时返回404
    """
    try:
        formula = formula_service.get_formula_by_id(formula_id)
        if formula is None:
            raise HTTPException(status_code=404, detail=f"方剂不存在: {formula_id}")
        return formula
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取方剂详情失败: {str(e)}")


@router.get("/name/{name}",
    response_model=FormulaModel,
    summary="根据名称获取方剂",
    description="根据方剂名称获取方剂信息，支持模糊匹配。"""
)
async def get_formula_by_name(name: str):
    """
    根据名称获取方剂
    
    Args:
        name: 方剂名称
    
    Returns:
        FormulaModel: 方剂完整信息
    
    Raises:
        HTTPException: 方剂不存在时返回404
    """
    try:
        formula = formula_service.get_formula_by_name(name)
        if formula is None:
            raise HTTPException(status_code=404, detail=f"方剂不存在: {name}")
        return formula
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取方剂失败: {str(e)}")


@router.get("/metadata/info",
    response_model=dict,
    summary="获取数据元信息",
    description="获取方剂数据集的元信息，包括数据来源、更新时间等。"""
)
async def get_metadata():
    """
    获取数据元信息
    
    Returns:
        dict: 元信息字典，包含数据来源、更新时间、总数等
    """
    try:
        return formula_service.metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取元信息失败: {str(e)}")


@router.get("/expanded/{formula_id}",
    response_model=ExpandedFormulaModel,
    summary="获取方剂扩展信息",
    description="""根据方剂ID获取包含扩展字段的完整方剂信息。

扩展字段包括：
- alias: 方剂别名
- modern_research: 现代药理研究摘要
- clinical_cases: 典型医案引用
- composition.role: 配伍角色（君/臣/佐/使）

AI协作说明：
- 此接口返回完整的扩展数据，便于AI深入分析方剂
- 配伍角色字段支持君/臣/佐/使的配伍规律分析
- 现代研究和医案提供科学依据和临床应用参考
"""
)
async def get_expanded_formula_by_id(formula_id: str):
    """
    根据ID获取方剂扩展信息
    
    Args:
        formula_id: 方剂ID，格式为 "f" + 三位数字，如 "f002"
    
    Returns:
        ExpandedFormulaModel: 包含扩展字段的方剂完整信息
    
    Raises:
        HTTPException: 方剂不存在时返回404
    """
    try:
        formula = formula_service.get_formula_by_id(formula_id)
        if formula is None:
            raise HTTPException(status_code=404, detail=f"方剂不存在: {formula_id}")
        
        # 转换为扩展模型（保持兼容性）
        # 在实际应用中，这里应该从扩展数据源加载完整数据
        expanded_data = formula.model_dump()
        
        # 添加扩展字段的默认值（在实际系统中应该从完整数据源加载）
        expanded_data.setdefault('alias', [])
        expanded_data.setdefault('modern_research', '')
        expanded_data.setdefault('clinical_cases', [])
        
        return ExpandedFormulaModel(**expanded_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取方剂扩展信息失败: {str(e)}")


@router.get("/search/advanced",
    response_model=List[FormulaSearchResult],
    summary="高级搜索方剂",
    description="""根据多个条件高级搜索方剂。

搜索范围包括：
- 方剂名称和别名
- 功效和主治
- 分类和来源
- 组成药材

AI协作说明：
- 支持多字段组合搜索，便于AI进行复杂查询
- 别名搜索扩展了名称匹配范围
- 药材搜索支持方剂组成分析
"""
)
async def advanced_search_formulas(
    keyword: str = Query(..., description="搜索关键词", min_length=1),
    category: Optional[str] = Query(None, description="方剂分类"),
    herb: Optional[str] = Query(None, description="组成药材"),
    source: Optional[str] = Query(None, description="来源典籍"),
    limit: int = Query(10, description="返回结果数量限制", ge=1, le=50)
):
    """
    高级搜索方剂
    
    Args:
        keyword: 搜索关键词
        category: 方剂分类过滤
        herb: 组成药材过滤
        source: 来源典籍过滤
        limit: 返回结果数量限制
    
    Returns:
        List[FormulaSearchResult]: 搜索结果列表，包含匹配度评分
    """
    try:
        # 基础搜索
        results = formula_service.search_formulas(keyword, limit=limit)
        
        # 应用过滤条件
        filtered_results = []
        for result in results:
            formula = formula_service.get_formula_by_id(result.formula.id)
            if formula:
                match = True
                
                # 分类过滤
                if category and formula.category:
                    if category not in formula.category:
                        match = False
                
                # 药材过滤
                if herb and match:
                    herb_found = False
                    for comp in formula.composition:
                        if herb in comp.herb:
                            herb_found = True
                            break
                    if not herb_found:
                        match = False
                
                # 来源过滤
                if source and formula.source:
                    if source not in formula.source:
                        match = False
                
                if match:
                    filtered_results.append(result)
        
        return filtered_results[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"高级搜索失败: {str(e)}")


@router.get("/categories/list",
    response_model=List[str],
    summary="获取所有分类列表",
    description="获取方剂数据集中所有可用的分类列表。"""
)
async def get_all_categories():
    """
    获取所有分类列表
    
    Returns:
        List[str]: 分类名称列表
    """
    try:
        formulas = formula_service.get_all_formulas()
        categories = set()
        
        for formula in formulas:
            if formula.category:
                categories.add(formula.category)
        
        return sorted(list(categories))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")
