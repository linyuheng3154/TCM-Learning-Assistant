"""
模型验证测试 - Model Validation Tests

本模块测试数据模型的验证功能和扩展模型的兼容性。

AI协作说明：
- 测试确保数据模型能够正确处理各种输入情况
- 验证扩展模型与基础模型的兼容性
- 确保Schema验证机制正常工作
"""

import pytest
from src.models.formula import (
    HerbComposition,
    ExpandedHerbComposition,
    FormulaModel,
    ExpandedFormulaModel,
    FormulaBriefModel
)


class TestHerbComposition:
    """测试药材组成模型"""
    
    def test_basic_herb_composition(self):
        """测试基础药材组成模型"""
        comp = HerbComposition(herb="麻黄", dosage="9g")
        assert comp.herb == "麻黄"
        assert comp.dosage == "9g"
        assert comp.note is None
    
    def test_herb_composition_with_note(self):
        """测试带备注的药材组成模型"""
        comp = HerbComposition(herb="桂枝", dosage="6g", note="去皮")
        assert comp.herb == "桂枝"
        assert comp.dosage == "6g"
        assert comp.note == "去皮"


class TestExpandedHerbComposition:
    """测试扩展药材组成模型"""
    
    def test_expanded_herb_composition(self):
        """测试扩展药材组成模型"""
        comp = ExpandedHerbComposition(
            herb="桂枝", 
            dosage="6g", 
            role="君",
            note="去皮"
        )
        assert comp.herb == "桂枝"
        assert comp.dosage == "6g"
        assert comp.role == "君"
        assert comp.note == "去皮"
    
    def test_expanded_herb_compatibility(self):
        """测试扩展模型与基础模型的兼容性"""
        # 扩展模型应该能够接受基础模型的所有字段
        base_comp = HerbComposition(herb="麻黄", dosage="9g")
        expanded_comp = ExpandedHerbComposition(**base_comp.model_dump())
        
        assert expanded_comp.herb == "麻黄"
        assert expanded_comp.dosage == "9g"
        assert expanded_comp.role is None


class TestFormulaModel:
    """测试方剂基础模型"""
    
    def test_basic_formula_creation(self):
        """测试基础方剂模型创建"""
        formula = FormulaModel(
            id="f001",
            name="麻黄汤",
            composition=[
                HerbComposition(herb="麻黄", dosage="9g")
            ],
            efficacy="发汗解表，宣肺平喘",
            indications="外感风寒表实证",
            source="《伤寒论》"
        )
        
        assert formula.id == "f001"
        assert formula.name == "麻黄汤"
        assert len(formula.composition) == 1
        assert formula.efficacy == "发汗解表，宣肺平喘"
        assert formula.source == "《伤寒论》"
    
    def test_formula_with_optional_fields(self):
        """测试包含可选字段的方剂模型"""
        formula = FormulaModel(
            id="f002",
            name="桂枝汤",
            pinyin="guizhi tang",
            composition=[
                HerbComposition(herb="桂枝", dosage="9g")
            ],
            efficacy="解肌发表，调和营卫",
            indications="外感风寒表虚证",
            source="《伤寒论》",
            category="解表剂-辛温解表"
        )
        
        assert formula.pinyin == "guizhi tang"
        assert formula.category == "解表剂-辛温解表"


class TestExpandedFormulaModel:
    """测试扩展方剂模型"""
    
    def test_expanded_formula_creation(self):
        """测试扩展方剂模型创建"""
        formula = ExpandedFormulaModel(
            id="f001",
            name="麻黄汤",
            alias=["麻黄解表汤"],
            composition=[
                ExpandedHerbComposition(herb="麻黄", dosage="9g", role="君")
            ],
            efficacy="发汗解表，宣肺平喘",
            indications="外感风寒表实证",
            source="《伤寒论》",
            modern_research="麻黄碱具有中枢兴奋作用",
            clinical_cases=["《伤寒论》原文应用"]
        )
        
        assert formula.id == "f001"
        assert formula.alias == ["麻黄解表汤"]
        assert formula.modern_research == "麻黄碱具有中枢兴奋作用"
        assert formula.clinical_cases == ["《伤寒论》原文应用"]
        assert formula.composition[0].role == "君"
    
    def test_expanded_formula_compatibility(self):
        """测试扩展模型与基础模型的兼容性"""
        # 基础模型数据应该能够转换为扩展模型
        base_formula = FormulaModel(
            id="f002",
            name="桂枝汤",
            composition=[
                HerbComposition(herb="桂枝", dosage="9g")
            ],
            efficacy="解肌发表，调和营卫",
            indications="外感风寒表虚证",
            source="《伤寒论》"
        )
        
        # 转换为扩展模型
        expanded_data = base_formula.model_dump()
        expanded_data['alias'] = []
        expanded_data['modern_research'] = ''
        expanded_data['clinical_cases'] = []
        
        expanded_formula = ExpandedFormulaModel(**expanded_data)
        
        assert expanded_formula.id == "f002"
        assert expanded_formula.name == "桂枝汤"
        assert expanded_formula.alias == []
        assert expanded_formula.modern_research == ""


class TestFormulaBriefModel:
    """测试方剂简要模型"""
    
    def test_brief_model_creation(self):
        """测试简要模型创建"""
        brief = FormulaBriefModel(
            id="f001",
            name="麻黄汤",
            efficacy="发汗解表，宣肺平喘",
            category="解表剂-辛温解表"
        )
        
        assert brief.id == "f001"
        assert brief.name == "麻黄汤"
        assert brief.efficacy == "发汗解表，宣肺平喘"
        assert brief.category == "解表剂-辛温解表"


class TestDataValidation:
    """测试数据验证功能"""
    
    def test_required_fields_validation(self):
        """测试必填字段验证"""
        # 缺少必填字段应该报错
        with pytest.raises(ValueError):
            FormulaModel(
                id="f001",
                # 缺少 name
                composition=[],
                efficacy="",
                indications="",
                source=""
            )
    
    def test_composition_validation(self):
        """测试组成字段验证"""
        # 组成列表不能为空
        with pytest.raises(ValueError):
            FormulaModel(
                id="f001",
                name="测试方剂",
                composition=[],  # 空列表
                efficacy="功效",
                indications="主治",
                source="来源"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])