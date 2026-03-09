#!/bin/bash

# TCM-Learning-Assistant 开发脚本

echo "🚀 TCM Learning Assistant 开发环境设置"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ Python3 环境正常"

# 安装依赖
echo "📦 安装项目依赖..."
pip install -r requirements.txt

# 检查环境配置
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，创建示例配置..."
    cp .env.example .env
    echo "📝 请编辑 .env 文件配置 OpenAI API Key"
fi

echo "🎉 开发环境设置完成!"
echo ""
echo "下一步:"
echo "1. 编辑 .env 文件配置 API Key"
echo "2. 运行: uvicorn src.main:app --reload"
echo "3. 访问: http://localhost:8000/docs"