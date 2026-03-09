"""
方剂API接口 - Formula API Endpoints

本模块提供方剂相关的REST API接口，包括：
1. 方剂列表查询
2. 方剂详情查询
3. 方剂搜索
4. 基于症状的方剂推荐

API文档：
- 所有接口返回JSON格式数据
- 错误响应格式：{"error": "错误信息", "code": 错误码}
- 成功响应格式：{"data": 数据, "message": "成功信息"}

AI协作说明：
- 每个接口都有详细的说明文档，可通过 /docs 查看
- 接口命名遵循RESTful规范
- 响应数据使用 Pydantic 模型进行序列化
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from src.models.formula import FormulaModel, FormulaBriefModel, FormulaSearchResult
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
