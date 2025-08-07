# 知识图谱构建系统

## 项目简介

这是一个基于Web的知识图谱构建平台，支持从文本中自动抽取实体和关系，构建结构化的知识图谱，并提供可视化展示功能。

## 系统架构

### 后端 (FastAPI)
- **端口**: 8000
- **技术栈**: Python, FastAPI, Uvicorn
- **功能**: 提供RESTful API，处理知识图谱构建任务

### 前端 (React + TypeScript)
- **端口**: 3002
- **技术栈**: React, TypeScript, Ant Design
- **功能**: 用户界面，配置管理，任务监控，图谱可视化

## 主要功能

### 1. 主体定义 (Subject Definition)
- 本体定义
- 实体类型管理
- 关系类型管理

### 2. 知识抽取 (Knowledge Extraction)
- 文本预处理
- 实体抽取
- 关系抽取
- 模式学习

### 3. 知识映射 (Knowledge Mapping)
- 实体映射
- 关系映射
- 本体映射
- 相似度计算

### 4. 知识融合 (Knowledge Fusion)
- 实体融合
- 关系融合
- 冲突解决
- 知识图谱构建

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 8+

### 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd frontend
npm install
```

### 启动服务

#### 方式一：使用启动脚本（推荐）
```bash
cd kg_web
./start_services.sh
```

#### 方式二：手动启动

**启动后端服务:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端服务:**
```bash
cd frontend
PORT=3002 npm start
```

### 访问地址

- **前端界面**: http://localhost:3002
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 使用指南

### 1. 首页
- 输入要处理的文本内容
- 可以使用示例数据快速体验
- 点击"开始构建知识图谱"创建任务

### 2. 配置管理
- 调整知识抽取参数
- 配置映射和融合规则
- 设置可视化选项

### 3. 任务管理
- 查看任务执行状态和进度
- 监控任务运行情况
- 查看任务详情和结果

### 4. 图谱可视化
- 查看知识图谱可视化结果
- 分析实体和关系数据
- 下载图谱图片

## API接口

### 配置管理
- `GET /api/config` - 获取当前配置
- `POST /api/config` - 更新配置

### 任务管理
- `POST /api/tasks/create` - 创建知识图谱构建任务
- `GET /api/tasks` - 获取所有任务
- `GET /api/tasks/{task_id}` - 获取任务状态
- `DELETE /api/tasks/{task_id}` - 删除任务

### 数据获取
- `GET /api/sample-data` - 获取示例数据
- `GET /api/knowledge-graph/{task_id}` - 获取知识图谱数据
- `GET /api/visualization/{task_id}` - 获取可视化图片

## 项目结构

```
kg_web/
├── backend/                 # 后端服务
│   ├── main.py             # FastAPI应用主文件
│   ├── requirements.txt    # Python依赖
│   └── static/             # 静态文件目录
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── pages/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   ├── services/       # API服务
│   │   ├── types/          # 类型定义
│   │   └── App.tsx         # 主应用组件
│   ├── package.json        # npm依赖配置
│   └── public/             # 静态资源
├── start_services.sh       # 服务启动脚本
└── README.md              # 项目说明
```

## 技术特性

### 后端特性
- ✅ RESTful API设计
- ✅ 异步任务处理
- ✅ 跨域支持
- ✅ 自动API文档生成
- ✅ 错误处理和日志记录

### 前端特性
- ✅ 响应式设计
- ✅ TypeScript类型安全
- ✅ 组件化架构
- ✅ 路由管理
- ✅ 状态管理

### 知识图谱功能
- ✅ 中文文本处理
- ✅ 实体识别和抽取
- ✅ 关系抽取
- ✅ 图谱可视化
- ✅ 配置灵活调整

## 开发说明

### 后端开发
- 使用FastAPI框架
- 集成kg_core核心模块
- 支持异步任务处理
- 提供完整的API文档

### 前端开发
- 基于React + TypeScript
- 使用Ant Design组件库
- 支持多页面路由
- 响应式布局设计

## 故障排除

### 常见问题

1. **端口被占用**
   - 前端默认端口3002，如被占用可修改`package.json`中的PORT配置
   - 后端默认端口8000，可在启动命令中修改

2. **依赖安装失败**
   - 确保Python和Node.js版本满足要求
   - 检查网络连接，可能需要配置镜像源

3. **API调用失败**
   - 检查后端服务是否正常启动
   - 确认CORS配置是否正确

## 版本历史

- **v1.0.0** - 初始版本
  - 基础知识图谱构建功能
  - Web界面支持
  - 任务管理和监控
  - 图谱可视化

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库
- 发送邮件至项目维护者