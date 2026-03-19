# TCM-Learning-Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen.svg)]()

**中医学习助手** - 结合传统中医知识与现代 Web 技术的开源学习工具，提供方剂查询、药材知识管理和前端交互界面。

## 功能特性

### 已完成功能 ✅

| 功能 | 描述 |
|------|------|
| **方剂库** | 100首经典方剂，支持分类筛选、拼音搜索、详情展示、方剂变化对比 |
| **药材库** | 342味药材数据，包含功效、主治、性味归经、用法用量等 |
| **前端界面** | 响应式单页应用，深色主题，支持方剂/药材搜索与详情展示 |
| **数据完善** | 31首方剂经典原文、25首煎服法、689条炮制信息 |
| **拼音搜索** | 支持汉字、拼音全拼、拼音首字母搜索 |
| **配伍禁忌** | 方剂配伍禁忌检查功能 |
| **RESTful API** | 完整的后端 API 接口，支持 Swagger 文档 |

### 开发中功能 🔶

| 功能 | 描述 |
|------|------|
| **AI辅助辨证** | 基于症状的智能辨证推荐（开发验证中） |

## 技术栈

- **后端**: FastAPI + Python 3.9+
- **前端**: HTML5 + CSS3 + Vanilla JavaScript（无框架依赖）
- **数据库**: SQLite
- **数据格式**: JSON
- **容器化**: Docker + Docker Compose

## 快速开始

### 方式一：本地运行

```bash
# 克隆仓库
git clone https://github.com/linyuheng3154/TCM-Learning-Assistant.git
cd TCM-Learning-Assistant

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/ui 打开前端界面。

### 方式二：Docker 部署

```bash
# 克隆仓库
git clone https://github.com/linyuheng3154/TCM-Learning-Assistant.git
cd TCM-Learning-Assistant

# 构建并运行
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问 http://localhost:8000/ui 打开前端界面。

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/formulas` | GET | 获取方剂列表 |
| `/formulas/{formula_id}` | GET | 获取方剂详情 |
| `/formulas/search` | GET | 搜索方剂 |
| `/herbs` | GET | 获取药材列表 |
| `/herbs/{herb_id}` | GET | 获取药材详情 |
| `/herbs/search` | GET | 搜索药材 |

## 项目结构

```
TCM-Learning-Assistant/
├── data/                   # 数据文件
│   ├── formulas.json       # 方剂数据
│   ├── herbs.json          # 药材数据
│   └── tcm.db              # SQLite 数据库
├── frontend/               # 前端文件
│   ├── index.html          # 单页应用入口
│   ├── styles.css          # 样式文件
│   └── app.js              # 前端逻辑
├── src/                    # 后端源码
│   ├── main.py             # FastAPI 应用入口
│   ├── api/                # API 路由
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑
│   └── config/             # 配置文件
├── tests/                  # 测试文件
├── docs/                   # 文档
├── Dockerfile              # Docker 构建文件
├── docker-compose.yml      # Docker Compose 配置
└── requirements.txt        # Python 依赖
```

## 数据来源

本项目数据来源于以下中医经典著作：
- 《伤寒论》
- 《金匮要略》
- 《神农本草经》
- 《方剂学》教材

所有数据均经过人工校对，力求准确可靠。

## 开发路线

详见 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

## 贡献指南

欢迎贡献代码、报告问题或提出建议！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 贡献方式
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

感谢所有为中医知识数字化做出贡献的开源项目和开发者。

---

**维护者**: [@linyuheng3154](https://github.com/linyuheng3154)

如果你觉得这个项目有帮助，欢迎 ⭐ Star 支持！
