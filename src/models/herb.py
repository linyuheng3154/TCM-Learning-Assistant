"""
药材数据模型 - Herb Data Models

本模块定义了中药材相关的数据结构，用于：
1. 药材知识库的数据存储和检索
2. 方剂组成中单味药材的详细信息
3. 药材功效与症状的关联分析

数据来源：中国药典（2020版）

AI协作说明：
- HerbModel: 完整的药材信息模型
- HerbBriefModel: 简要信息模型
- 性味归经使用传统中医术语，便于专业用户理解

注意事项：
- contraindications 字段包含重要的用药安全信息，AI 在推荐药材时必须检查
- dosage 字段仅供参考，实际用量需遵医嘱
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class HerbModel(BaseModel):
    """
    药材完整信息模型
    
    这是药材数据的核心模型，包含药材的所有属性信息。
    
    字段说明：
        - id: 药材唯一标识符，格式为 "h" + 三位数字
        - name: 药材名称（中文正名）
        - pinyin: 拼音名称
        - alias: 别名列表（如"国老"为甘草别名）
        - nature: 性味（如"甘、辛，温"）
        - meridian: 归经（如"心、肺、脾经"）
        - efficacy: 功效
        - indications: 主治
        - dosage: 用量范围
        - contraindications: 禁忌症和注意事项
        - source: 数据来源
    """
    id: str = Field(..., description="药材唯一标识")
    name: str = Field(..., description="药材名称")
    pinyin: Optional[str] = Field(None, description="拼音名称")
    alias: List[str] = Field(default_factory=list, description="别名列表")
    nature: str = Field(..., description="性味")
    meridian: str = Field(..., description="归经")
    efficacy: str = Field(..., description="功效")
    indications: str = Field(..., description="主治")
    dosage: Optional[str] = Field(None, description="用量")
    contraindications: Optional[str] = Field(None, description="禁忌")
    source: Optional[str] = Field(None, description="来源")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "h003",
                "name": "人参",
                "pinyin": "renshen",
                "alias": ["棒槌", "山参"],
                "nature": "甘、微苦，微温",
                "meridian": "脾、肺、心、肾经",
                "efficacy": "大补元气，复脉固脱，补脾益肺，生津养血，安神益智",
                "indications": "体虚欲脱，脾虚食少，肺虚喘咳等",
                "dosage": "3-9g",
                "source": "中国药典"
            }
        }


class HerbBriefModel(BaseModel):
    """
    药材简要信息模型
    
    用于列表展示和方剂组成预览。
    """
    id: str
    name: str
    nature: str
    efficacy: str


class HerbSearchResult(BaseModel):
    """
    药材搜索结果模型
    
    包含匹配度评分。
    """
    herb: HerbBriefModel
    score: float = Field(..., ge=0, le=1, description="匹配度评分")
    matched_fields: List[str] = Field(default_factory=list, description="匹配字段")


# ============================================================
# 药材功效分类常量
# 用于辅助 AI 进行药材推荐和分类
# ============================================================

HERB_CATEGORIES = {
    "解表药": ["桂枝", "麻黄", "柴胡", "紫苏", "荆芥", "防风"],
    "清热药": ["黄芩", "黄连", "黄柏", "栀子", "石膏", "知母", "牡丹皮"],
    "泻下药": ["大黄", "芒硝", "番泻叶"],
    "祛风湿药": ["独活", "威灵仙", "木瓜", "秦艽"],
    "化湿药": ["苍术", "厚朴", "藿香", "佩兰"],
    "利水渗湿药": ["茯苓", "泽泻", "薏苡仁", "车前子"],
    "温里药": ["附子", "干姜", "肉桂", "吴茱萸"],
    "理气药": ["陈皮", "枳实", "枳壳", "木香", "香附"],
    "消食药": ["山楂", "神曲", "麦芽", "谷芽", "鸡内金"],
    "止血药": ["三七", "白及", "仙鹤草", "蒲黄"],
    "活血化瘀药": ["川芎", "丹参", "红花", "桃仁", "牛膝"],
    "化痰止咳平喘药": ["半夏", "天南星", "桔梗", "瓜蒌", "贝母", "杏仁"],
    "安神药": ["酸枣仁", "柏子仁", "远志", "龙骨", "牡蛎"],
    "平肝息风药": ["天麻", "钩藤", "石决明", "珍珠母"],
    "开窍药": ["麝香", "冰片", "石菖蒲"],
    "补虚药": ["人参", "黄芪", "白术", "甘草", "当归", "白芍", "熟地黄", "麦冬"],
    "收涩药": ["五味子", "乌梅", "山茱萸", "莲子"],
}

# 药性分类
HERB_NATURE_CATEGORIES = {
    "寒": ["黄连", "黄芩", "大黄", "栀子", "牡丹皮"],
    "凉": ["柴胡", "赤芍", "玄参"],
    "平": ["茯苓", "甘草", "天麻"],
    "温": ["桂枝", "麻黄", "人参", "黄芪", "当归", "白术", "陈皮", "半夏"],
    "热": ["附子", "干姜", "肉桂"],
}
