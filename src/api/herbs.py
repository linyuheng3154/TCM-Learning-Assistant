"""
药材API接口 - Herb API Endpoints

本模块提供药材相关的REST API接口，包括：
1. 药材列表查询
2. 药材详情查询
3. 药材搜索
4. 药材使用统计
5. 按性味/归经筛选

API文档：
- 所有接口返回JSON格式数据
- 错误响应格式：{"error": "错误信息", "code": 错误码}
- 成功响应格式：{"data": 数据, "message": "成功信息"}

AI协作说明：
- 每个接口都有详细的说明文档，可通过 /docs 查看
- 接口命名遵循RESTful规范
- 响应数据使用 Pydantic 模型进行序列化

数据来源：
- 中国药典（2020版）
- 《神农本草经》
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from src.models.herb import (
    HerbModel,
    HerbBriefModel,
    HerbSearchResult
)
from src.services.herb_service import herb_service


# 创建路由器
router = APIRouter(
    prefix="/herbs",
    tags=["药材管理"],
    responses={
        404: {"description": "药材不存在"},
        500: {"description": "服务器内部错误"}
    }
)


@router.get("/",
    response_model=List[HerbBriefModel],
    summary="获取药材列表",
    description="""获取所有药材的简要信息列表。

返回数据包含：
- id: 药材唯一标识
- name: 药材名称
- nature: 性味
- efficacy: 功效（截取前50字）

可用于：
- 药材列表页面展示
- 下拉选择框数据源
"""
)
async def get_all_herbs():
    """
    获取所有药材列表
    
    Returns:
        List[HerbBriefModel]: 药材简要信息列表
    """
    try:
        return herb_service.get_all_herbs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取药材列表失败: {str(e)}")


@router.get("/search",
    response_model=List[HerbSearchResult],
    summary="搜索药材",
    description="""根据关键词搜索药材。

搜索范围：
- 药材名称（权重最高）
- 拼音名称
- 别名
- 功效
- 主治

返回结果按匹配度评分排序。
"""
)
async def search_herbs(
    keyword: str = Query(..., description="搜索关键词", min_length=1),
    limit: int = Query(10, description="返回结果数量限制", ge=1, le=50)
):
    """
    搜索药材
    
    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制
    
    Returns:
        List[HerbSearchResult]: 搜索结果列表，包含匹配度评分
    """
    try:
        results = herb_service.search_herbs(keyword, limit=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/{herb_id}",
    response_model=HerbModel,
    summary="获取药材详情",
    description="根据药材ID获取完整的药材信息。"
)
async def get_herb_by_id(herb_id: str):
    """
    根据ID获取药材详情
    
    Args:
        herb_id: 药材ID，格式为 "h" + 三位数字，如 "h003"
    
    Returns:
        HerbModel: 药材完整信息
    
    Raises:
        HTTPException: 药材不存在时返回404
    """
    try:
        herb = herb_service.get_herb_by_id(herb_id)
        if herb is None:
            raise HTTPException(status_code=404, detail=f"药材不存在: {herb_id}")
        return herb
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取药材详情失败: {str(e)}")


@router.get("/name/{name}",
    response_model=HerbModel,
    summary="根据名称获取药材",
    description="根据药材名称获取药材信息，支持别名查询。"
)
async def get_herb_by_name(name: str):
    """
    根据名称获取药材
    
    Args:
        name: 药材名称或别名
    
    Returns:
        HerbModel: 药材完整信息
    
    Raises:
        HTTPException: 药材不存在时返回404
    """
    try:
        herb = herb_service.get_herb_by_name(name)
        if herb is None:
            raise HTTPException(status_code=404, detail=f"药材不存在: {name}")
        return herb
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取药材失败: {str(e)}")


@router.get("/stats/{herb_name}",
    response_model=dict,
    summary="获取药材使用统计",
    description="""获取药材在方剂中的使用情况统计。

统计内容包括：
- 使用频次：该药材出现在多少首方剂中
- 所在方剂：列出使用该药材的方剂
- 配伍角色分布：君/臣/佐/使的比例

可用于：
- 分析药材的常用程度
- 了解药材的配伍规律
"""
)
async def get_herb_stats(herb_name: str):
    """
    获取药材使用统计
    
    Args:
        herb_name: 药材名称
    
    Returns:
        Dict: 统计信息
    """
    try:
        stats = herb_service.get_herb_stats(herb_name)
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/nature/{nature}",
    response_model=List[HerbBriefModel],
    summary="按性味筛选药材",
    description="""按性味获取药材列表。

常见性味：
- 温：桂枝、麻黄、人参等
- 寒：黄连、黄芩、大黄等
- 平：茯苓、甘草、天麻等
- 凉：柴胡、赤芍等
- 热：附子、干姜、肉桂等
"""
)
async def get_herbs_by_nature(nature: str):
    """
    按性味获取药材列表
    
    Args:
        nature: 性味关键词，如 "温"、"寒"、"平"
    
    Returns:
        List[HerbBriefModel]: 符合条件的药材列表
    """
    try:
        return herb_service.get_herbs_by_nature(nature)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取药材列表失败: {str(e)}")


@router.get("/meridian/{meridian}",
    response_model=List[HerbBriefModel],
    summary="按归经筛选药材",
    description="""按归经获取药材列表。

常见归经：
- 肺经：麻黄、桂枝、杏仁等
- 脾经：人参、白术、茯苓等
- 心经：桂枝、黄连、人参等
- 肝经：柴胡、白芍、当归等
- 肾经：附子、肉桂、熟地等
"""
)
async def get_herbs_by_meridian(meridian: str):
    """
    按归经获取药材列表
    
    Args:
        meridian: 归经关键词，如 "肺"、"脾"、"肾"
    
    Returns:
        List[HerbBriefModel]: 符合条件的药材列表
    """
    try:
        return herb_service.get_herbs_by_meridian(meridian)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取药材列表失败: {str(e)}")


@router.get("/metadata/info",
    response_model=dict,
    summary="获取数据元信息",
    description="获取药材数据集的元信息，包括数据来源、更新时间等。"
)
async def get_metadata():
    """
    获取数据元信息
    
    Returns:
        dict: 元信息字典，包含数据来源、更新时间、总数等
    """
    try:
        return herb_service.metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取元信息失败: {str(e)}")
