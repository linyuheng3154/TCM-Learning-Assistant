"""
TCM-Learning-Assistant FastAPI应用入口

本项目是一个中医学习助手，结合传统中医知识与现代AI技术。

主要功能：
1. 方剂智能查询系统 - 查询方剂组成、功效、主治等信息
2. 药材知识管理系统 - 管理中药材的性味归经、功效主治
3. AI辅助辨证分析 - 根据症状推荐方剂（规划中）

API文档：
- Swagger UI: /docs
- ReDoc: /redoc

技术栈：
- FastAPI: 现代高性能Python Web框架
- Pydantic: 数据验证和序列化
- AI技术: 自然语言处理能力集成（规划中）

AI协作说明：
- 本文件是应用入口，负责初始化FastAPI应用和注册路由
- 所有API路由都在 src/api/ 目录下
- 数据模型在 src/models/ 目录下
- 业务逻辑在 src/services/ 目录下
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.config.settings import get_settings
from src.api import formulas

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="""
## 中医学习助手 API

结合传统中医知识与现代AI技术的开源项目。

### 核心功能
- 🏥 **方剂智能查询** - 查询方剂组成、功效、主治等信息
- 📚 **药材知识管理** - 管理中药材的性味归经、功效主治
- 🧠 **AI辅助辨证** - 根据症状推荐方剂（开发中）

### 数据来源
- 中国药典
- 经典医籍（如《伤寒论》《太平惠民和剂局方》）
- LingdanLLM 开源数据集

### 开源协议
MIT License
""",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 注册路由
# ============================================================

app.include_router(formulas.router)


# ============================================================
# 根路由和健康检查
# ============================================================

@app.get("/",
    summary="API首页",
    description="返回API基本信息"
)
async def root():
    """
    API首页
    
    返回API的基本信息，包括名称、版本、状态等。
    """
    return {
        "message": "TCM Learning Assistant API",
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "formulas": "/formulas",
            "search": "/formulas/search?keyword=桂枝",
            "health": "/health"
        }
    }


@app.get("/health",
    summary="健康检查",
    description="检查服务是否正常运行"
)
async def health_check():
    """
    健康检查端点
    
    用于监控系统检查服务状态。
    """
    return {
        "status": "healthy",
        "version": settings.version
    }


# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
