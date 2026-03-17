"""
配伍禁忌检查 API - Herb Compatibility Check API

检查中药配伍禁忌的 REST API 接口。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from src.services.herb_compatibility_service import (
    herb_compatibility_service,
    CompatibilityCheckResult,
    ContraindicationWarning
)


router = APIRouter(prefix="/compatibility", tags=["配伍禁忌检查"])


class HerbCheckRequest(BaseModel):
    """药材配伍检查请求"""
    herbs: List[str] = Field(..., description="药材列表", min_length=1)
    is_pregnant: bool = Field(default=False, description="是否孕妇")


class FormulaCheckRequest(BaseModel):
    """方剂配伍检查请求"""
    formula_id: str = Field(..., description="方剂ID")
    is_pregnant: bool = Field(default=False, description="是否孕妇")


@router.post("/check/herbs", response_model=CompatibilityCheckResult)
async def check_herb_compatibility(request: HerbCheckRequest):
    """
    检查药材配伍禁忌
    
    检查传入的药材列表是否存在配伍禁忌：
    - 十八反：剧烈毒性反应
    - 十九畏：药效相互抑制
    - 妊娠禁忌（可选）：孕妇禁用/慎用药物
    
    Args:
        request: 包含药材列表和是否孕妇标志
    
    Returns:
        CompatibilityCheckResult: 检查结果，包含是否安全和警告列表
    
    Example:
        POST /compatibility/check/herbs
        {
            "herbs": ["甘草", "大戟", "芫花"],
            "is_pregnant": false
        }
    """
    try:
        result = herb_compatibility_service.check_herbs(
            herbs=request.herbs,
            is_pregnant=request.is_pregnant
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check/formula", response_model=CompatibilityCheckResult)
async def check_formula_compatibility(request: FormulaCheckRequest):
    """
    检查方剂配伍禁忌
    
    检查指定方剂是否存在配伍禁忌，包括方剂中所有药材的组合。
    
    Args:
        request: 包含方剂ID和是否孕妇标志
    
    Returns:
        CompatibilityCheckResult: 检查结果
    
    Example:
        POST /compatibility/check/formula
        {
            "formula_id": "f001",
            "is_pregnant": true
        }
    """
    try:
        result = herb_compatibility_service.check_formula(
            formula_id=request.formula_id,
            is_pregnant=request.is_pregnant
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verse/shiba-fan")
async def get_shiba_fan_verse():
    """
    获取十八反歌诀
    
    返回传统的十八反记忆歌诀，便于学习和背诵。
    """
    verse = herb_compatibility_service.get_shiba_fan_verse()
    return {
        "name": "十八反歌诀",
        "verse": verse,
        "source": "《本草经集注》"
    }


@router.get("/verse/shijiu-wei")
async def get_shijiu_wei_verse():
    """
    获取十九畏歌诀
    
    返回传统的十九畏记忆歌诀，便于学习和背诵。
    """
    verse = herb_compatibility_service.get_shijiu_wei_verse()
    return {
        "name": "十九畏歌诀",
        "verse": verse,
        "source": "《本草纲目》引《药性赋》"
    }
