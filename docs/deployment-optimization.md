# TCM项目一键部署和配置优化方案

## 🚀 一键部署脚本设计

### 📦 基础部署脚本
```bash
#!/bin/bash
# deploy-tcm.sh

set -e

echo "🚀 开始部署TCM-Learning-Assistant..."

# 检查依赖
echo "📋 检查系统依赖..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git未安装，请先安装Git"
    exit 1
fi

# 创建项目目录
echo "📁 创建项目目录..."
PROJECT_DIR="$HOME/tcm-assistant"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 克隆项目
echo "📥 克隆项目代码..."
git clone https://github.com/linyuheng3154/TCM-Learning-Assistant.git .

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 创建配置文件
echo "⚙️ 创建配置文件..."
cat > config.yaml << EOF
# TCM-Learning-Assistant 配置文件
version: "1.0.0"

# 数据配置
data:
  formulas_path: "./data/formulas.json"
  herbs_path: "./data/herbs.json"
  
# API配置
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  
# 模型配置
model:
  default: "gpt-4"
  fallback: "gpt-3.5-turbo"
  
# 安全配置
security:
  cors_origins:
    - "http://localhost:3000"
    - "http://127.0.0.1:3000"
  rate_limit: 100
EOF

echo "✅ 配置文件创建完成"

# 初始化数据
echo "📊 初始化数据..."
python3 -c "
from src.services.formula_service import formula_service
print(f'📚 加载方剂数据: {len(formula_service.get_all_formulas())} 首')
"

# 启动服务
echo "🚀 启动TCM服务..."
python3 src/main.py &

# 等待服务启动
sleep 3

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ TCM服务启动成功！"
    echo "🌐 访问地址: http://localhost:8000"
    echo "📚 API文档: http://localhost:8000/docs"
else
    echo "❌ 服务启动失败，请检查日志"
    exit 1
fi

echo ""
echo "🎉 TCM-Learning-Assistant 部署完成！"
echo ""
echo "📖 使用说明："
echo "   1. 访问 http://localhost:8000/docs 查看API文档"
echo "   2. 使用 curl 或 Postman 测试API接口"
echo "   3. 查看 logs/app.log 获取详细日志"
echo ""
```

### 🔧 智能体部署脚本
```bash
#!/bin/bash
# deploy-agents.sh

echo "👥 开始部署TCM智能体..."

# 创建智能体目录
AGENTS_DIR="$HOME/tcm-assistant/agents"
mkdir -p $AGENTS_DIR

# 部署诊断大厨
echo "👨⚕️ 部署诊断大厨..."
cp -r ./tcm-assistants/chefs/diagnosis-chef $AGENTS_DIR/

# 部署方剂大厨
echo "🌿 部署方剂大厨..."
cp -r ./tcm-assistants/chefs/formula-chef $AGENTS_DIR/

# 部署药材大厨
echo "💊 部署药材大厨..."
cp -r ./tcm-assistants/chefs/herb-chef $AGENTS_DIR/

# 部署典籍大厨
echo "📚 部署典籍大厨..."
cp -r ./tcm-assistants/chefs/classic-chef $AGENTS_DIR/

# 部署养生大厨
echo "🧘 部署养生大厨..."
cp -r ./tcm-assistants/chefs/wellness-chef $AGENTS_DIR/

# 创建智能体配置
cat > $AGENTS_DIR/agents.yaml << EOF
# TCM智能体配置
version: "1.0.0"

agents:
  diagnosis:
    name: "诊断大厨"
    enabled: true
    config_path: "./diagnosis-chef/config.yaml"
    
  formula:
    name: "方剂大厨"
    enabled: true
    config_path: "./formula-chef/config.yaml"
    
  herb:
    name: "药材大厨"
    enabled: true
    config_path: "./herb-chef/config.yaml"
    
  classic:
    name: "典籍大厨"
    enabled: true
    config_path: "./classic-chef/config.yaml"
    
  wellness:
    name: "养生大厨"
    enabled: true
    config_path: "./wellness-chef/config.yaml"

routing:
  default: "formula"
  rules:
    - pattern: ".*诊断.*|.*症状.*|.*辨证.*"
      agent: "diagnosis"
    - pattern: ".*方剂.*|.*配伍.*|.*君臣.*"
      agent: "formula"
    - pattern: ".*药材.*|.*性味.*|.*归经.*"
      agent: "herb"
    - pattern: ".*经典.*|.*医案.*|.*文献.*"
      agent: "classic"
    - pattern: ".*养生.*|.*食疗.*|.*预防.*"
      agent: "wellness"
EOF

echo "✅ 智能体部署完成！"
echo "📋 已部署智能体："
echo "   👨⚕️ 诊断大厨 - 中医诊断专家"
echo "   🌿 方剂大厨 - 方剂学专家"
echo "   💊 药材大厨 - 中药学专家"
echo "   📚 典籍大厨 - 经典文献专家"
echo "   🧘 养生大厨 - 养生保健专家"
```

## ⚙️ 配置优化方案

### 统一配置管理
```yaml
# config/tcm-config.yaml
version: "1.0.0"

# 数据源配置
data_sources:
  formulas:
    path: "./data/formulas.json"
    schema: "./schemas/formula-schema.json"
    auto_reload: true
    
  herbs:
    path: "./data/herbs.json"
    schema: "./schemas/herb-schema.json"
    auto_reload: true
    
  classics:
    path: "./data/classics.json"
    schema: "./schemas/classic-schema.json"
    auto_reload: true

# API配置
api:
  server:
    host: "0.0.0.0"
    port: 8000
    workers: 4
    
  docs:
    enabled: true
    title: "TCM Learning Assistant API"
    description: "中医学习助手API接口"
    
  security:
    cors_origins:
      - "http://localhost:3000"
      - "http://127.0.0.1:3000"
      - "https://tcm-assistant.com"
    rate_limit_per_minute: 100

# 智能体配置
agents:
  enabled: true
  config_path: "./agents/agents.yaml"
  
  # 智能体权限
  permissions:
    diagnosis:
      allowed_tools:
        - "symptom_analysis"
        - "tongue_diagnosis"
        - "pulse_diagnosis"
        - "constitution_identification"
        
    formula:
      allowed_tools:
        - "formula_search"
        - "compatibility_analysis"
        - "formula_modification"
        - "clinical_cases"

# 模型配置
models:
  default: "gpt-4"
  fallback: "gpt-3.5-turbo"
  
  # 模型特定配置
  gpt-4:
    max_tokens: 4000
    temperature: 0.7
    
  gpt-3.5-turbo:
    max_tokens: 2000
    temperature: 0.7

# 日志配置
logging:
  level: "INFO"
  file: "./logs/tcm.log"
  max_size: "100MB"
  backup_count: 5
  
  # 审计日志
  audit:
    enabled: true
    file: "./logs/audit.log"

# 缓存配置
cache:
  enabled: true
  backend: "redis"  # 或 "memory"
  
  redis:
    host: "localhost"
    port: 6379
    db: 0
    
  memory:
    max_size: "100MB"
    ttl: 3600  # 1小时
```

### 环境特定配置
```bash
#!/bin/bash
# setup-env.sh

ENV=$1

case $ENV in
  "development")
    echo "设置开发环境..."
    export TCM_ENV=development
    export TCM_DEBUG=true
    export TCM_LOG_LEVEL=DEBUG
    ;;
  "production")
    echo "设置生产环境..."
    export TCM_ENV=production
    export TCM_DEBUG=false
    export TCM_LOG_LEVEL=INFO
    ;;
  "testing")
    echo "设置测试环境..."
    export TCM_ENV=testing
    export TCM_DEBUG=true
    export TCM_LOG_LEVEL=DEBUG
    ;;
  *)
    echo "用法: $0 <environment>"
    echo "可用环境: development, production, testing"
    exit 1
    ;;
esac

echo "✅ 环境设置完成: $ENV"
```

## 🎯 部署优势

### 用户体验提升
- **一键部署**: 用户无需了解技术细节即可完成部署
- **环境自适应**: 自动检测和配置系统环境
- **错误处理**: 详细的错误提示和解决方案

### 运维效率提升
- **配置集中管理**: 所有配置在统一文件中管理
- **环境隔离**: 开发、测试、生产环境独立配置
- **自动化运维**: 脚本化部署和配置

### 系统稳定性
- **依赖检查**: 部署前自动检查系统依赖
- **服务监控**: 自动检查服务状态
- **日志管理**: 统一的日志配置和管理

---

**总结**: 通过一键部署和配置优化，TCM项目可以大幅降低用户使用门槛，提升部署效率和系统稳定性，为大规模应用奠定基础。