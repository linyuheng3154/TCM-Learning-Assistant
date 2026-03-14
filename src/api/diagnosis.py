"""
中医辨证推荐API接口 - TCM Diagnosis API Endpoints

本模块提供中医辨证推荐的REST API接口，包括：
1. 基于症状的辨证推荐
2. 证型查询
3. 推荐结果解释

AI协作说明：
- 核心功能：症状输入 → 证型识别 → 方剂推荐
- 支持批量症状输入
- 返回结构化推荐结果

免责声明：
本功能仅供学习和参考，不能替代专业医生的诊断。
如有健康问题，请咨询专业中医师。
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.services.diagnosis_service import diagnosis_service, DiagnosisResult

# 创建限流器
limiter = Limiter(key_func=get_remote_address)


# 创建路由器
router = APIRouter(
    prefix="/diagnosis",
    tags=["辨证推荐"],
    responses={
        404: {"description": "资源不存在"},
        500: {"description": "服务器内部错误"}
    }
)


# ============================================================
# 请求/响应模型
# ============================================================

class DiagnosisRequest(BaseModel):
    """辨证推荐请求"""
    symptoms: List[str] = Field(
        ...,
        description="症状列表",
        min_length=1,
        example=["发热", "恶寒", "无汗", "头痛"]
    )
    top_k: int = Field(
        default=3,
        description="返回前K个匹配结果",
        ge=1,
        le=10
    )
    min_score: float = Field(
        default=0.1,
        description="最低匹配分数阈值",
        ge=0.0,
        le=1.0
    )


class SyndromeMatchResponse(BaseModel):
    """证型匹配响应"""
    syndrome_id: str = Field(description="证型ID")
    syndrome_name: str = Field(description="证型名称")
    description: str = Field(description="证型描述")
    matched_keywords: List[str] = Field(description="匹配的症状关键词")
    score: float = Field(description="匹配分数 (0.0-1.0)")


class RecommendedFormulaResponse(BaseModel):
    """推荐方剂响应"""
    id: str = Field(description="方剂ID")
    name: str = Field(description="方剂名称")
    efficacy: str = Field(description="功效")
    indications: str = Field(description="主治")
    matched_syndrome: str = Field(description="匹配的证型")
    match_score: float = Field(description="匹配分数")
    matched_keywords: List[str] = Field(description="匹配的症状关键词")
    source: str = Field(description="出处")


class DiagnosisResponse(BaseModel):
    """辨证推荐响应"""
    symptoms: List[str] = Field(description="输入的症状列表")
    matched_syndromes: List[SyndromeMatchResponse] = Field(description="匹配的证型列表")
    recommended_formulas: List[RecommendedFormulaResponse] = Field(description="推荐的方剂列表")
    confidence: float = Field(description="整体置信度 (0.0-1.0)")
    disclaimer: str = Field(description="免责声明")


# ============================================================
# API端点
# ============================================================

@router.post("/recommend",
    response_model=DiagnosisResponse,
    summary="辨证推荐",
    description="""根据症状进行中医辨证，推荐相应的方剂。

**工作流程：**
1. 症状解析与标准化
2. 证型识别与匹配
3. 方剂智能推荐
4. 返回推荐结果与解释

**注意事项：**
- 输入症状越详细，推荐越准确
- 建议输入3个以上症状
- 本功能仅供学习参考，不能替代专业医生诊断
"""
)
@limiter.limit("10/minute")
async def recommend_formulas(request: Request, diagnosis_request: DiagnosisRequest):
    """
    辨证推荐
    
    Args:
        diagnosis_request: 包含症状列表的请求
    
    Returns:
        DiagnosisResponse: 辨证推荐结果
    """
    try:
        result = diagnosis_service.diagnose(
            symptoms=diagnosis_request.symptoms,
            top_k=diagnosis_request.top_k,
            min_score=diagnosis_request.min_score
        )
        
        # 转换为响应模型
        return DiagnosisResponse(
            symptoms=result.symptoms,
            matched_syndromes=[
                SyndromeMatchResponse(
                    syndrome_id=m.syndrome_id,
                    syndrome_name=m.syndrome_name,
                    description=m.description,
                    matched_keywords=m.matched_keywords,
                    score=m.score
                )
                for m in result.matched_syndromes
            ],
            recommended_formulas=[
                RecommendedFormulaResponse(**f)
                for f in result.recommended_formulas
            ],
            confidence=result.confidence,
            disclaimer=result.disclaimer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"辨证推荐失败: {str(e)}")


@router.get("/recommend",
    response_model=DiagnosisResponse,
    summary="辨证推荐 (GET方式)",
    description="通过GET参数进行辨证推荐，适合简单查询场景。"
)
@limiter.limit("10/minute")
async def recommend_formulas_get(
    request: Request,
    symptoms: str = Query(
        ...,
        description="症状列表，用逗号分隔",
        example="发热,恶寒,无汗,头痛"
    ),
    top_k: int = Query(3, description="返回前K个匹配结果", ge=1, le=10),
    min_score: float = Query(0.1, description="最低匹配分数阈值", ge=0.0, le=1.0)
):
    """
    辨证推荐 (GET方式)
    
    Args:
        symptoms: 逗号分隔的症状列表
        top_k: 返回前K个匹配结果
        min_score: 最低匹配分数阈值
    
    Returns:
        DiagnosisResponse: 辨证推荐结果
    """
    try:
        symptom_list = [s.strip() for s in symptoms.split(",") if s.strip()]
        
        if not symptom_list:
            raise HTTPException(status_code=400, detail="请输入症状")
        
        result = diagnosis_service.diagnose(
            symptoms=symptom_list,
            top_k=top_k,
            min_score=min_score
        )
        
        return DiagnosisResponse(
            symptoms=result.symptoms,
            matched_syndromes=[
                SyndromeMatchResponse(
                    syndrome_id=m.syndrome_id,
                    syndrome_name=m.syndrome_name,
                    description=m.description,
                    matched_keywords=m.matched_keywords,
                    score=m.score
                )
                for m in result.matched_syndromes
            ],
            recommended_formulas=[
                RecommendedFormulaResponse(**f)
                for f in result.recommended_formulas
            ],
            confidence=result.confidence,
            disclaimer=result.disclaimer
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"辨证推荐失败: {str(e)}")


@router.get("/syndromes",
    response_model=List[dict],
    summary="获取所有证型列表",
    description="获取系统支持的所有证型信息。"
)
async def get_all_syndromes():
    """
    获取所有证型列表
    
    Returns:
        List[dict]: 证型信息列表
    """
    try:
        return diagnosis_service.get_all_syndromes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取证型列表失败: {str(e)}")


@router.get("/syndromes/{syndrome_id}",
    response_model=dict,
    summary="获取证型详情",
    description="根据证型ID获取详细信息。"
)
async def get_syndrome_by_id(syndrome_id: str):
    """
    获取证型详情
    
    Args:
        syndrome_id: 证型ID
    
    Returns:
        dict: 证型详细信息
    """
    try:
        syndrome = diagnosis_service.get_syndrome_by_id(syndrome_id)
        if syndrome is None:
            raise HTTPException(status_code=404, detail=f"证型不存在: {syndrome_id}")
        return syndrome
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取证型详情失败: {str(e)}")
