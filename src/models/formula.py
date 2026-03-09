"""
方剂数据模型 - Formula Data Models

本模块定义了中医方剂相关的数据结构，用于：
1. API 请求/响应的数据验证和序列化
2. 数据库存储结构的映射
3. 前端展示数据的格式化

数据来源：中国药典、经典医籍（如《伤寒论》《太平惠民和剂局方》等）

AI协作说明：
- FormulaModel: 完整的方剂信息模型，包含所有字段
- FormulaBriefModel: 简要信息模型，用于列表展示
- FormulaSearchResult: 搜索结果模型，包含匹配度评分

字段命名遵循中医传统术语，同时提供英文别名以便国际化。
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class HerbComposition(BaseModel):
    """
    方剂组成中的单味药材
    
    Attributes:
        herb: 药材名称（中文）
        dosage: 用量（如 "9g"、"适量"、"3枚"）
        note: 备注（可选，如炮制方法、特殊用法）
    """
    herb: str = Field(..., description="药材名称")
    dosage: str = Field(..., description="用量")
    note: Optional[str] = Field(None, description="备注说明")


class FormulaModel(BaseModel):
    """
    方剂完整信息模型
    
    这是方剂数据的核心模型，包含方剂的所有属性信息。
    用于 API 响应和详细查询结果。
    
    字段说明：
        - id: 方剂唯一标识符，格式为 "f" + 三位数字
        - name: 方剂名称（中文正名）
        - pinyin: 拼音名称，便于模糊搜索
        - composition: 组成药材列表
        - efficacy: 功效主治概述
        - indications: 详细主治病症
        - contraindications: 禁忌症和注意事项
        - usage: 用法用量
        - source: 来源典籍或药典
        - category: 方剂分类（可选，如"解表剂-辛温解表"）
    """
    id: str = Field(..., description="方剂唯一标识")
    name: str = Field(..., description="方剂名称")
    pinyin: Optional[str] = Field(None, description="拼音名称")
    composition: List[HerbComposition] = Field(default_factory=list, description="组成药材")
    efficacy: str = Field(..., description="功效")
    indications: str = Field(..., description="主治")
    contraindications: Optional[str] = Field(None, description="禁忌")
    usage: Optional[str] = Field(None, description="用法用量")
    source: Optional[str] = Field(None, description="来源")
    category: Optional[str] = Field(None, description="方剂分类")
    
    # 中成药特有字段
    is_prescription: Optional[bool] = Field(None, description="是否为处方药")
    is_patent_medicine: Optional[bool] = Field(None, description="是否为中成药")
    specification: Optional[str] = Field(None, description="规格")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "f002",
                "name": "桂枝汤",
                "pinyin": "guizhi tang",
                "composition": [
                    {"herb": "桂枝", "dosage": "9g"},
                    {"herb": "芍药", "dosage": "9g"}
                ],
                "efficacy": "解肌发表，调和营卫",
                "indications": "外感风寒表虚证",
                "source": "《伤寒论》",
                "category": "解表剂-辛温解表"
            }
        }


class FormulaBriefModel(BaseModel):
    """
    方剂简要信息模型
    
    用于列表展示和搜索结果预览，仅包含最核心的信息。
    可减少数据传输量，提升响应速度。
    """
    id: str
    name: str
    efficacy: str
    category: Optional[str] = None


class FormulaSearchResult(BaseModel):
    """
    方剂搜索结果模型
    
    包含匹配度评分，用于搜索结果的排序和展示。
    
    Attributes:
        formula: 方剂简要信息
        score: 匹配度评分（0-1），越高表示越匹配
        matched_fields: 匹配的字段列表，如 ["name", "efficacy"]
    """
    formula: FormulaBriefModel
    score: float = Field(..., ge=0, le=1, description="匹配度评分")
    matched_fields: List[str] = Field(default_factory=list, description="匹配字段")
