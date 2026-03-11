# TCM技能包模块化设计方案

## 🧂 中医专业技能包体系

### 📋 **诊断技能包 - Diagnosis Pack**
**功能范围**: 中医诊断相关的所有能力

**包含模块**:
- **四诊模块**: 望闻问切数据采集和分析
- **辨证模块**: 八纲辨证、脏腑辨证等
- **体质模块**: 九种体质辨识和评估
- **舌诊模块**: 舌象分析和解读
- **脉诊模块**: 脉象分析和解读

**配置示例**:
```yaml
name: "诊断技能包"
description: "中医诊断全套工具"
version: "1.0.0"

modules:
  four_diagnosis:
    enabled: true
    capabilities:
      - "inspection"      # 望诊
      - "listening"       # 闻诊
      - "questioning"     # 问诊
      - "palpation"       # 切诊
  
  syndrome_differentiation:
    enabled: true
    capabilities:
      - "eight_principles"  # 八纲辨证
      - "zangfu"           # 脏腑辨证
      - "six_channels"     # 六经辨证
      - "wei_qi_ying_xue"  # 卫气营血辨证
  
  constitution:
    enabled: true
    capabilities:
      - "nine_types"       # 九种体质
      - "assessment"       # 体质评估
      - "adjustment"       # 体质调理
```

### 💊 **方剂技能包 - Formula Pack**
**功能范围**: 方剂相关的所有能力

**包含模块**:
- **经典方剂模块**: 《伤寒论》《金匮要略》等经典方剂
- **现代方剂模块**: 现代临床应用和研究成果
- **配伍分析模块**: 君臣佐使配伍规律分析
- **加减化裁模块**: 方剂加减和个性化调整
- **医案参考模块**: 典型医案和应用场景

**配置示例**:
```yaml
name: "方剂技能包"
description: "中医方剂全套工具"
version: "1.0.0"

modules:
  classic_formulas:
    enabled: true
    sources:
      - "伤寒论"
      - "金匮要略"
      - "温病条辨"
      - "太平惠民和剂局方"
  
  compatibility_analysis:
    enabled: true
    capabilities:
      - "sovereign_minister_assistant_courier"  # 君臣佐使
      - "herb_interactions"                     # 药材相互作用
      - "dosage_optimization"                   # 剂量优化
  
  formula_modification:
    enabled: true
    capabilities:
      - "addition_subtraction"                  # 加减
      - "dosage_adjustment"                     # 剂量调整
      - "herb_replacement"                      # 药材替换
```

### 🌿 **药材技能包 - Herb Pack**
**功能范围**: 中药材相关的所有能力

**包含模块**:
- **药材属性模块**: 性味归经、功效主治
- **配伍禁忌模块**: 十八反十九畏等配伍禁忌
- **剂量用法模块**: 常用剂量和特殊用法
- **炮制方法模块**: 各种炮制方法和作用
- **质量鉴别模块**: 真伪优劣鉴别方法

**配置示例**:
```yaml
name: "药材技能包"
description: "中药材全套工具"
version: "1.0.0"

modules:
  herb_properties:
    enabled: true
    properties:
      - "nature_flavor"     # 性味
      - "meridian_tropism"  # 归经
      - "efficacy"          # 功效
      - "indications"       # 主治
  
  compatibility_taboos:
    enabled: true
    taboos:
      - "eighteen_incompatibles"    # 十八反
      - "nineteen_fears"            # 十九畏
      - "pregnancy_contraindicated" # 妊娠禁忌
  
  processing_methods:
    enabled: true
    methods:
      - "cleaning"          # 净制
      - "cutting"           # 切制
      - "stir-frying"       # 炒制
      - "calcining"         # 煅制
      - "steaming"          # 蒸制
```

### 📚 **典籍技能包 - Classic Pack**
**功能范围**: 中医经典文献相关能力

**包含模块**:
- **文献检索模块**: 经典文献原文检索
- **医案解读模块**: 古代医案现代解读
- **学说比较模块**: 各家学说比较分析
- **源流考证模块**: 学术源流和历史沿革
- **现代应用模块**: 经典理论的现代应用

**配置示例**:
```yaml
name: "典籍技能包"
description: "中医经典文献全套工具"
version: "1.0.0"

modules:
  classic_retrieval:
    enabled: true
    sources:
      - "黄帝内经"
      - "伤寒杂病论"
      - "金匮要略"
      - "温病条辨"
      - "本草纲目"
  
  medical_cases:
    enabled: true
    capabilities:
      - "case_interpretation"       # 医案解读
      - "modern_application"        # 现代应用
      - "diagnosis_analysis"        # 诊断分析
      - "treatment_evaluation"      # 治疗评价
```

## 🔧 技能包集成方案

### 技能包目录结构
```
tcm-skills/
├── diagnosis-pack/
│   ├── config.yaml
│   ├── modules/
│   │   ├── four_diagnosis.py
│   │   ├── syndrome_differentiation.py
│   │   └── constitution.py
│   └── examples/
│       ├── symptom_analysis.md
│       └── tongue_diagnosis.md
├── formula-pack/
│   ├── config.yaml
│   ├── modules/
│   │   ├── classic_formulas.py
│   │   ├── compatibility_analysis.py
│   │   └── formula_modification.py
│   └── examples/
│       ├── formula_search.md
│       └── herb_interactions.md
├── herb-pack/
│   ├── config.yaml
│   ├── modules/
│   │   ├── herb_properties.py
│   │   ├── compatibility_taboos.py
│   │   └── processing_methods.py
│   └── examples/
│       ├── herb_search.md
│       └── dosage_guidance.md
└── classic-pack/
    ├── config.yaml
    ├── modules/
    │   ├── classic_retrieval.py
    │   └── medical_cases.py
    └── examples/
        ├── literature_search.md
        └── case_study.md
```

### 技能包安装脚本
```bash
#!/bin/bash
# tcm-skill-install.sh

SKILL_PACK=$1
TARGET_DIR="./tcm-skills"

case $SKILL_PACK in
  "diagnosis")
    echo "安装诊断技能包..."
    cp -r ./skill-packs/diagnosis-pack $TARGET_DIR/
    ;;
  "formula")
    echo "安装方剂技能包..."
    cp -r ./skill-packs/formula-pack $TARGET_DIR/
    ;;
  "herb")
    echo "安装药材技能包..."
    cp -r ./skill-packs/herb-pack $TARGET_DIR/
    ;;
  "classic")
    echo "安装典籍技能包..."
    cp -r ./skill-packs/classic-pack $TARGET_DIR/
    ;;
  "all")
    echo "安装所有技能包..."
    cp -r ./skill-packs/* $TARGET_DIR/
    ;;
  *)
    echo "用法: $0 <skill-pack>"
    echo "可用技能包: diagnosis, formula, herb, classic, all"
    exit 1
    ;;
esac

echo "✅ 技能包安装完成！"
```

## 🎯 实施优势

### 模块化优势
- **按需安装**: 用户可以根据需要选择安装的技能包
- **独立升级**: 每个技能包可以独立更新和优化
- **专业聚焦**: 每个技能包专注于特定领域

### 技术优势
- **配置驱动**: YAML配置统一管理功能开关
- **权限控制**: 每个技能包有独立的权限设置
- **兼容性**: 技能包之间互不干扰

### 用户体验
- **简单安装**: 一键脚本完成技能包安装
- **灵活组合**: 可以自由组合需要的技能包
- **专业深度**: 每个技能包提供专业级功能

---

**总结**: 通过技能包模块化设计，TCM项目可以实现功能的灵活组合和按需扩展，大幅提升系统的可维护性和用户体验。