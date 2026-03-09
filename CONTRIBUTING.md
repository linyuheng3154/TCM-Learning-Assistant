# 贡献指南

感谢您对TCM-Learning-Assistant项目的关注！我们欢迎各种形式的贡献。

## 开发环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/linyuheng3154/TCM-Learning-Assistant.git
cd TCM-Learning-Assistant
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 环境配置
创建 `.env` 文件并配置：
```bash
OPENAI_API_KEY=your_openai_api_key
```

### 4. 启动开发服务器
```bash
uvicorn src.main:app --reload
```

## 开发规范

### 代码质量
- 保持代码清晰可读
- 添加必要的注释说明
- 为关键功能编写测试

### 提交规范  
- 提交信息清晰描述更改内容
- 示例：`添加方剂查询接口` 或 `修复药材数据验证`

### 测试要求
- 为核心功能编写测试
- 运行测试：`pytest tests/`

## 简单协作
- 直接沟通需求和问题
- 需要时创建相关文档
- 保持代码和文档的同步更新

## 项目结构

```
src/
├── api/           # API接口层
├── services/      # 业务逻辑层  
├── models/        # 数据模型层
├── data/          # 数据文件
└── config/        # 配置管理

tests/             # 测试文件
docs/              # 项目文档
data/              # 数据目录
```

## 联系方式

- GitHub Issues: 报告问题和功能请求
- 项目讨论区: 技术讨论和方案设计

## 行为准则

请遵守开源社区的行为准则，保持友好和专业的交流环境。