"""
方剂数据模型 - Formula Data Models

本模块定义了中医方剂相关的数据结构，用于：
1. API 请求/响应的数据验证和序列化
2. 数据库存储结构的映射
3. 前端展示数据的格式化

数据来源：中国药典、经典医籍（如《伤寒论》《金匮要略》《太平惠民和剂局方》等）

AI协作说明：
- FormulaModel: 完整的方剂信息模型，包含所有字段
- ExpandedHerbComposition: 扩展的药材组成模型，包含配伍角色
- FormulaBriefModel: 简要信息模型，用于列表展示
- FormulaSearchResult: 搜索结果模型，包含匹配度评分
- ExpandedFormulaModel: 扩展的方剂模型，支持现代研究和医案

字段命名遵循中医传统术语，同时提供英文别名以便国际化。

重要更新说明：
- 2026-03-10: 扩展数据模型支持50首经典方剂数据库
- 新增字段：alias, modern_research, clinical_cases
- 扩展组成字段：role, note (配伍角色和炮制说明)
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class HerbComposition(BaseModel):
    """
    方剂组成中的单味药材
    
    AI协作说明：
    - 这是基础的药材组成模型，包含必要的信息
    - 用于简单的方剂数据，保持向后兼容
    
    Attributes:
        herb: 药材名称（中文）
        dosage: 用量（如 "9g"、"适量"、"3枚"）
        note: 备注（可选，如炮制方法、特殊用法）
    """
    herb: str = Field(..., description="药材名称")
    dosage: str = Field(..., description="用量")
    note: Optional[str] = Field(None, description="备注说明")


class ExpandedHerbComposition(HerbComposition):
    """
    扩展的药材组成模型 - 包含配伍角色信息
    
    AI协作说明：
    - 这是扩展模型，用于50首经典方剂数据库
    - 包含配伍角色（君/臣/佐/使），便于AI理解方剂结构
    - 保持与基础模型的兼容性，可以混合使用
    
    使用场景：
    - 经典方剂的详细分析
    - 配伍规律研究
    - 教学和学术用途
    
    Attributes:
        role: 配伍角色（君药/臣药/佐药/使药）
        note: 扩展的备注信息（炮制、特殊用法等）
    """
    role: Optional[str] = Field(None, description="配伍角色：君/臣/佐/使")
    # note字段从父类继承，这里可以扩展更多说明


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
    pinyin_initials: Optional[str] = Field(None, description="拼音首字母（如 'gzt' 代表桂枝汤）")
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
    
    model_config = ConfigDict(
        json_schema_extra={
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
    )
    
    @field_validator('composition')
    @classmethod
    def validate_composition_not_empty(cls, v: List[HerbComposition]) -> List[HerbComposition]:
        """验证组成药材列表不能为空"""
        if not v:
            raise ValueError('组成药材列表不能为空')
        return v


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


class ExpandedFormulaModel(FormulaModel):
    """
    扩展的方剂完整信息模型 - 支持50首经典方剂数据库
    
    AI协作说明：
    - 这是FormulaModel的扩展版本，用于经典方剂的详细数据
    - 新增字段支持现代研究和临床应用信息
    - 保持与基础模型的兼容性，可以平滑升级
    
    扩展字段说明：
    - alias: 方剂别名，便于多名称搜索
    - modern_research: 现代药理研究摘要，便于AI理解科学依据
    - clinical_cases: 典型医案引用，提供临床应用参考
    
    使用场景：
    - 经典方剂的学术研究
    - 临床应用的参考
    - 教学和科普展示
    """
    alias: List[str] = Field(
        default_factory=list,
        description="方剂别名列表，便于多名称搜索"
    )
    modern_research: Optional[str] = Field(
        None,
        description="现代药理研究摘要，包含主要成分和作用机制"
    )
    clinical_cases: List[str] = Field(
        default_factory=list,
        description="典型医案引用，提供临床应用参考"
    )
    
    # 使用扩展的药材组成模型
    # composition字段从父类继承，可以包含ExpandedHerbComposition对象
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "f002",
                "name": "桂枝汤",
                "pinyin": "guizhi tang",
                "alias": ["阳旦汤"],
                "composition": [
                    {"herb": "桂枝", "dosage": "9g", "role": "君", "note": "去皮"},
                    {"herb": "芍药", "dosage": "9g", "role": "臣"},
                    {"herb": "甘草", "dosage": "6g", "role": "佐"},
                    {"herb": "生姜", "dosage": "9g", "role": "佐"},
                    {"herb": "大枣", "dosage": "12枚", "role": "使"}
                ],
                "efficacy": "解肌发表，调和营卫",
                "indications": "外感风寒表虚证",
                "source": "《伤寒论》",
                "category": "解表剂-辛温解表",
                "modern_research": "桂枝汤具有解热、抗炎、免疫调节等作用...",
                "clinical_cases": [
                    "《伤寒论》原文：太阳中风，阳浮而阴弱...",
                    "现代应用：用于感冒、流感、产后发热等"
                ]
            }
        }
    )


class FormulaCompareRequest(BaseModel):
    """
    方剂对比请求模型
    
    用于请求对比多首方剂的信息。
    
    Attributes:
        formula_ids: 要对比的方剂ID列表，最多5个
    """
    formula_ids: List[str] = Field(
        ...,
        description="要对比的方剂ID列表",
        min_length=2,
        max_length=5
    )


class HerbCompareResult(BaseModel):
    """
    药材对比结果模型
    
    显示各方剂中该药材的使用情况。
    
    Attributes:
        herb: 药材名称
        usage: 各方剂中的用量 {方剂ID: 用量}
        roles: 各方剂中的配伍角色 {方剂ID: 角色}
    """
    herb: str = Field(..., description="药材名称")
    usage: dict = Field(default_factory=dict, description="各方剂中的用量")
    roles: dict = Field(default_factory=dict, description="各方剂中的配伍角色")


class FormulaCompareResult(BaseModel):
    """
    方剂对比结果模型
    
    包含多方剂的详细对比信息。
    
    Attributes:
        formulas: 参与对比的方剂简要信息
        herbs_comparison: 药材对比结果（共同药材和差异）
        efficacy_comparison: 功效对比
        indications_comparison: 主治对比
        contraindications_comparison: 禁忌对比
        summary: 对比摘要
    """
    formulas: List[FormulaBriefModel] = Field(..., description="参与对比的方剂")
    herbs_comparison: List[HerbCompareResult] = Field(
        default_factory=list,
        description="药材对比结果"
    )
    common_herbs: List[str] = Field(
        default_factory=list,
        description="共同药材"
    )
    unique_herbs: dict = Field(
        default_factory=dict,
        description="各方剂独有药材 {方剂ID: [药材列表]}"
    )
    efficacy_comparison: dict = Field(
        default_factory=dict,
        description="功效对比 {方剂ID: 功效}"
    )
    indications_comparison: dict = Field(
        default_factory=dict,
        description="主治对比 {方剂ID: 主治}"
    )
    contraindications_comparison: dict = Field(
        default_factory=dict,
        description="禁忌对比 {方剂ID: 禁忌}"
    )
    summary: str = Field(
        default="",
        description="对比摘要"
    )


# ============================================================
# 方剂加减变化模型
# ============================================================

class HerbVariation(BaseModel):
    """
    单味药材的加减变化
    
    Attributes:
        herb: 药材名称
        action: 加减动作 (add/remove/modify)
        original_dosage: 原用量（可选）
        new_dosage: 新用量（可选）
        reason: 加减原因
    """
    herb: str = Field(..., description="药材名称")
    action: str = Field(..., description="加减动作: add(增加)/remove(减去)/modify(调整用量)")
    original_dosage: Optional[str] = Field(None, description="原用量")
    new_dosage: Optional[str] = Field(None, description="新用量")
    reason: str = Field(..., description="加减原因")


class FormulaVariation(BaseModel):
    """
    方剂加减变化
    
    Attributes:
        name: 变化后方剂名称
        base_formula_id: 基础方剂ID
        variations: 药材变化列表
        indication_change: 主治变化说明
        source: 出处
    """
    name: str = Field(..., description="变化后方剂名称")
    base_formula_id: str = Field(..., description="基础方剂ID")
    variations: List[HerbVariation] = Field(default_factory=list, description="药材变化列表")
    indication_change: str = Field(default="", description="主治变化说明")
    source: Optional[str] = Field(None, description="出处")


class FormulaVariationResult(BaseModel):
    """
    方剂加减变化查询结果
    
    Attributes:
        base_formula: 基础方剂信息
        variations: 变化列表（向上继承和向下衍生）
        inherited_from: 继承来源（该方剂是由哪个方剂加减而来）
        derived_to: 衍生方剂（该方剂加减变化后的方剂）
    """
    base_formula: FormulaBriefModel = Field(..., description="基础方剂信息")
    inherited_from: List[FormulaVariation] = Field(default_factory=list, description="继承来源")
    derived_to: List[FormulaVariation] = Field(default_factory=list, description="衍生方剂")
    total_variations: int = Field(default=0, description="变化总数")
