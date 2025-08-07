#!/bin/bash

# 知识图谱构建系统 - 服务启动脚本

echo "🚀 启动知识图谱构建系统..."

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装，请先安装Python"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装npm"
    exit 1
fi

echo "📦 检查依赖..."

# 安装后端依赖
echo "安装后端依赖..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 后端依赖安装失败"
    exit 1
fi

# 安装前端依赖
echo "安装前端依赖..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 前端依赖安装失败"
        exit 1
    fi
fi

echo "🎯 启动服务..."

# 启动后端服务
echo "启动后端API服务 (端口: 8000)..."
cd ../backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端服务
echo "启动前端界面服务 (端口: 3002)..."
cd ../frontend
PORT=3002 npm start &
FRONTEND_PID=$!

echo ""
echo "✅ 服务启动完成!"
echo ""
echo "📍 访问地址:"
echo "   前端界面: http://localhost:3002"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "🛑 停止服务请按 Ctrl+C"
echo ""

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ 服务已停止'; exit" INT

# 保持脚本运行
wait