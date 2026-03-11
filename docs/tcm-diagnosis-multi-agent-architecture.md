# 中医诊断多智能体架构设计方案

## 🏗️ 整体架构设计

### 核心设计理念
基于clawcooking的"龙虾烹饪"哲学：
- **去头去壳傻瓜式**: 复杂诊断过程自动化
- **十三香秘制调料**: 预打包的诊断技能组合
- **六位大厨掌勺**: 专业化分工的诊断智能体
- **本地厨房更放心**: 医疗数据本地化安全

### 架构总览
```
中医诊断多智能体系统
├── 🧠 诊断协调器 (Diagnosis Coordinator)
├── 👨⚕️ 四诊采集智能体 (Four Diagnosis Collector)
├── 🔍 辨证分析智能体 (Syndrome Analysis Agent)
├── 🩺 体质辨识智能体 (Constitution Identification Agent)
├── 💊 方剂推荐智能体 (Formula Recommendation Agent)
├── 🌿 药材配伍智能体 (Herb Compatibility Agent)
├── 📚 医案参考智能体 (Medical Case Reference Agent)
└── 🧘 养生建议智能体 (Wellness Advice Agent)
```

## 👥 智能体详细设计

### 🧠 **诊断协调器 (Diagnosis Coordinator)**
**角色**: 诊断流程总指挥，智能体调度中心

**核心功能**:
- 接收用户症状描述
- 调度合适的智能体处理
- 整合各智能体分析结果
- 生成最终诊断报告
- 管理诊断会话状态

**配置示例**:
```yaml
name: "诊断协调器"
description: "中医诊断流程总指挥"
version: "1.0.0"

capabilities:
  - "symptom_parsing"
  - "agent_routing"
  - "result_integration"
  - "report_generation"
  - "session_management"

routing_rules:
  - pattern: ".*症状.*|.*不舒服.*|.*疼痛.*"
    agent: "four_diagnosis"
  - pattern: ".*辨证.*|.*证候.*|.*病机.*"
    agent: "syndrome_analysis"
  - pattern: ".*体质.*|.*寒热.*|.*虚实.*"
    agent: "constitution_identification"
  - pattern: ".*方剂.*|.*开方.*|.*用药.*"
    agent: "formula_recommendation"
```

### 👨⚕️ **四诊采集智能体 (Four Diagnosis Collector)**
**角色**: 中医四诊（望闻问切）数据采集专家

**核心功能**:
- **望诊**: 面色、舌象、形体等视觉信息采集
- **闻诊**: 声音、气味等听觉嗅觉信息分析
- **问诊**: 症状、病史、生活习惯等信息收集
- **切诊**: 脉象分析和触诊信息处理

**交互流程**:
```yaml
interview_flow:
  step_1:
    type: "greeting"
    question: "您好！我是中医诊断助手，请问您哪里不舒服？"
  step_2:
    type: "symptom_collection"
    questions:
      - "主要症状是什么？"
      - "症状持续多久了？"
      - "什么情况下会加重或缓解？"
  step_3:
    type: "tongue_inquiry"
    question: "方便描述一下舌头的颜色和舌苔情况吗？"
  step_4:
    type: "pulse_inquiry"
    question: "您感觉脉搏是快还是慢？有力还是无力？"
  step_5:
    type: "constitution_inquiry"
    questions:
      - "平时怕冷还是怕热？"
      - "胃口怎么样？"
      - "睡眠质量如何？"
```

**数据模型**:
```python
class FourDiagnosisData:
    """四诊数据模型"""
    
    # 望诊
    inspection:
        complexion: str  # 面色
        tongue_color: str  # 舌色
        tongue_coating: str  # 舌苔
        body_shape: str  # 形体
    
    # 闻诊
    listening_smelling:
        voice: str  # 声音
        breath: str  # 呼吸
        odor: str  # 气味
    
    # 问诊
    questioning:
        main_symptoms: List[str]  # 主症
        duration: str  # 病程
        aggravating_factors: List[str]  # 加重因素
        relieving_factors: List[str]  # 缓解因素
    
    # 切诊
    palpation:
        pulse_type: str  # 脉象
        pulse_strength: str  # 脉力
        abdominal_examination: str  # 腹诊
```

### 🔍 **辨证分析智能体 (Syndrome Analysis Agent)**
**角色**: 中医辨证论治专家

**核心功能**:
- **八纲辨证**: 阴阳、表里、寒热、虚实
- **脏腑辨证**: 五脏六腑病机分析
- **六经辨证**: 太阳、阳明、少阳、太阴、少阴、厥阴
- **卫气营血辨证**: 温病辨证体系
- **气血津液辨证**: 气血津液病理分析

**辨证规则库**:
```yaml
differentiation_rules:
  # 八纲辨证规则
  eight_principles:
    yin_yang:
      pattern: ["畏寒", "肢冷", "面色苍白"]
      result: "阳虚"
    exterior_interior:
      pattern: ["恶寒", "发热", "头痛", "脉浮"]
      result: "表证"
  
  # 脏腑辨证规则
  zangfu:
    liver:
      pattern: ["胁痛", "易怒", "目赤"]
      result: "肝气郁结"
    spleen:
      pattern: ["纳差", "便溏", "乏力"]
      result: "脾虚"
  
  # 六经辨证规则
  six_channels:
    taiyang:
      pattern: ["恶寒", "发热", "头项强痛", "脉浮"]
      result: "太阳病"
    shaoyang:
      pattern: ["寒热往来", "口苦", "咽干", "目眩"]
      result: "少阳病"
```

### 🩺 **体质辨识智能体 (Constitution Identification Agent)**
**角色**: 中医体质辨识专家

**核心功能**:
- **九种体质辨识**: 平和质、气虚质、阳虚质等
- **体质评估问卷**: 标准化体质评估
- **体质调理建议**: 针对不同体质的养生指导
- **体质转化跟踪**: 体质变化趋势分析

**体质辨识模型**:
```yaml
constitution_types:
  peaceful:
    description: "阴阳平和，身体健康"
    characteristics:
      - "精力充沛"
      - "睡眠良好"
      - "胃口正常"
    
  qi_deficiency:
    description: "元气不足，容易疲劳"
    characteristics:
      - "容易疲劳"
      - "气短懒言"
      - "容易出汗"
    
  yang_deficiency:
    description: "阳气不足，畏寒怕冷"
    characteristics:
      - "畏寒肢冷"
      - "喜暖恶寒"
      - "小便清长"
```

### 💊 **方剂推荐智能体 (Formula Recommendation Agent)**
**角色**: 方剂学推荐专家

**核心功能**:
- **证候-方剂匹配**: 基于辨证结果推荐方剂
- **方剂加减化裁**: 根据具体症状调整方剂
- **剂量个性化**: 基于体质和病情调整剂量
- **禁忌检查**: 检查方剂配伍禁忌

**推荐算法**:
```python
class FormulaRecommender:
    """方剂推荐算法"""
    
    def recommend_formulas(self, syndrome: str, symptoms: List[str]) -> List[Formula]:
        """
        基于证候和症状推荐方剂
        """
        # 1. 证候匹配
        candidate_formulas = self.match_by_syndrome(syndrome)
        
        # 2. 症状权重匹配
        scored_formulas = self.score_by_symptoms(candidate_formulas, symptoms)
        
        # 3. 个性化调整
        personalized_formulas = self.personalize_formulas(scored_formulas)
        
        return personalized_formulas[:3]  # 返回前3个推荐
```

### 🌿 **药材配伍智能体 (Herb Compatibility Agent)**
**角色**: 药材配伍和禁忌检查专家

**核心功能**:
- **十八反检查**: 检查药材配伍禁忌
- **十九畏检查**: 检查药材相畏关系
- **剂量合理性**: 检查药材剂量是否合理
- **炮制建议**: 提供药材炮制方法建议

**配伍检查规则**:
```yaml
compatibility_rules:
  # 十八反
  eighteen_incompatibles:
    - herbs: ["甘草", "甘遂", "大戟", "芫花"]
      rule: "相反，不宜同用"
    - herbs: ["乌头", "贝母", "瓜蒌", "半夏", "白蔹", "白及"]
      rule: "相反，不宜同用"
  
  # 十九畏
  nineteen_fears:
    - herbs: ["硫黄", "朴硝"]
      rule: "相畏，不宜同用"
    - herbs: ["水银", "砒霜"]
      rule: "相畏，不宜同用"
```

### 📚 **医案参考智能体 (Medical Case Reference Agent)**
**角色**: 中医医案参考专家

**核心功能**:
- **相似医案检索**: 基于症状检索相似医案
- **经典医案解读**: 提供经典医案分析
- **治疗经验参考**: 提供治疗经验和注意事项
- **预后评估**: 基于医案提供预后参考

**医案数据库**:
```yaml
medical_cases:
  case_001:
    patient: "张某，男，45岁"
    symptoms:
      - "头痛发热"
      - "恶寒无汗"
      - "项背强几几"
    diagnosis: "太阳伤寒证"
    formula: "葛根汤"
    outcome: "服药2剂后症状缓解"
    
  case_002:
    patient: "李某，女，32岁"
    symptoms:
      - "心烦失眠"
      - "口干咽燥"
      - "舌红少苔"
    diagnosis: "阴虚火旺证"
    formula: "黄连阿胶汤"
    outcome: "服药1周后睡眠改善"
```

### 🧘 **养生建议智能体 (Wellness Advice Agent)**
**角色**: 中医养生保健专家

**核心功能**:
- **食疗建议**: 基于体质和证候的饮食指导
- **运动建议**: 适合的运动方式和强度
- **情志调养**: 情绪管理和心理调节
- **四季养生**: 不同季节的养生要点

**养生建议库**:
```yaml
wellness_advice:
  qi_deficiency:
    diet:
      - "多吃补气食物：山药、大枣、黄芪"
      - "避免生冷寒凉食物"
    exercise:
      - "适量运动：太极拳、八段锦"
      - "避免剧烈运动"
    lifestyle:
      - "保证充足睡眠"
      - "避免过度劳累"
```

## 🔧 技术实现方案

### 智能体通信协议
```python
class AgentMessage:
    """智能体间通信消息"""
    
    def __init__(self, sender: str, receiver: str, content: dict):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = datetime.now()

class DiagnosisSession:
    """诊断会话管理"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.patient_data = {}
        self.agent_results = {}
        self.final_report = None
```

### 诊断流程引擎
```python
class DiagnosisEngine:
    """诊断流程引擎"""
    
    def process_diagnosis(self, symptoms: str) -> DiagnosisReport:
        """处理诊断请求"""
        
        # 1. 症状解析
        parsed_symptoms = self.symptom_parser.parse(symptoms)
        
        # 2. 调度四诊采集
        four_diagnosis_data = self.four_diagnosis_agent.collect(parsed_symptoms)
        
        # 3. 调度辨证分析
        syndrome_result = self.syndrome_agent.analyze(four_diagnosis_data)
        
        # 4. 调度体质辨识
        constitution_result = self.constitution_agent.identify(four_diagnosis_data)
        
        # 5. 调度方剂推荐
        formula_recommendations = self.formula_agent.recommend(syndrome_result)
        
        # 6. 生成诊断报告
        report = self.generate_report(
            four_diagnosis_data,
            syndrome_result,
            constitution_result,
            formula_recommendations
        )
        
        return report
```

## 🎯 实施计划

### 第一阶段：核心智能体开发 (2周)
- [ ] 诊断协调器和四诊采集智能体
- [ ] 辨证分析智能体
- [ ] 方剂推荐智能体

### 第二阶段：扩展智能体开发 (2周)
- [ ] 体质辨识智能体
- [ ] 药材配伍智能体
- [ ] 医案参考智能体

### 第三阶段：系统集成 (1周)
- [ ] 智能体通信协议实现
- [ ] 诊断流程引擎开发
- [ ] 用户界面集成

## 📊 预期效果

### 用户体验
- **专业诊断**: 多位专家智能体协同诊断
- **个性化方案**: 基于体质和症状的定制方案
- **完整流程**: 从诊断到治疗到养生的完整服务

### 技术优势
- **模块化扩展**: 新增智能体不影响现有系统
- **专业深度**: 每个智能体专注于特定领域
- **协作智能**: 多智能体协作提供综合解决方案

---

**总结**: 基于clawcooking设计理念的中医诊断多智能体架构，实现了专业化分工、模块化设计和协作智能，为中医数字化诊断提供了完整的技术解决方案。