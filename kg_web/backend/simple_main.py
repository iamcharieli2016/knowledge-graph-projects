#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版后端服务，用于测试基础功能
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime

app = FastAPI(
    title="知识图谱构建API",
    description="知识图谱构建与可视化服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class Config(BaseModel):
    max_entities: int = 50
    similarity_threshold: float = 0.7
    extraction_method: str = "rule_based"
    language: str = "zh"

class TaskCreate(BaseModel):
    text: str
    config: Optional[Config] = None

class Task(BaseModel):
    id: str
    text: str
    status: str
    progress: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

# 全局变量存储
current_config = Config()
tasks_storage: Dict[str, Task] = {}
sample_texts = [
    "苹果公司是一家美国跨国科技公司，由史蒂夫·乔布斯、史蒂夫·沃兹尼亚克和罗纳德·韦恩于1976年创立。",
    "北京是中华人民共和国的首都，位于华北地区，是中国的政治、文化中心。",
    "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。"
]

@app.get("/")
async def root():
    return {"message": "知识图谱构建API服务", "version": "1.0.0"}

@app.get("/api/config")
async def get_config():
    return current_config

@app.post("/api/config")
async def update_config(config: Config):
    global current_config
    current_config = config
    return {"message": "配置更新成功", "config": current_config}

@app.get("/api/sample-data")
async def get_sample_data():
    return {
        "texts": sample_texts,
        "description": "示例文本数据，用于测试知识图谱构建"
    }

@app.post("/api/tasks/create")
async def create_task(task_data: TaskCreate, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    task = Task(
        id=task_id,
        text=task_data.text,
        status="pending",
        progress=0,
        created_at=datetime.now()
    )
    tasks_storage[task_id] = task
    
    # 启动后台任务
    background_tasks.add_task(process_kg_task, task_id)
    
    return {"task_id": task_id, "message": "任务已创建"}

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务不存在")
    return tasks_storage[task_id]

@app.get("/api/tasks")
async def list_tasks():
    return list(tasks_storage.values())

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务不存在")
    del tasks_storage[task_id]
    return {"message": "任务已删除"}

async def process_kg_task(task_id: str):
    """模拟知识图谱构建过程"""
    if task_id not in tasks_storage:
        return
    
    task = tasks_storage[task_id]
    
    try:
        # 模拟处理步骤
        steps = ["实体识别", "关系抽取", "知识映射", "图谱融合", "可视化生成"]
        
        for i, step in enumerate(steps):
            task.status = f"processing_{step}"
            task.progress = int((i + 1) / len(steps) * 100)
            tasks_storage[task_id] = task
            
            # 模拟处理时间
            import asyncio
            await asyncio.sleep(2)
        
        # 完成任务
        task.status = "completed"
        task.progress = 100
        task.completed_at = datetime.now()
        task.result = {
            "entities": ["苹果公司", "史蒂夫·乔布斯", "美国", "科技公司"],
            "relations": [
                {"source": "史蒂夫·乔布斯", "target": "苹果公司", "relation": "创立"},
                {"source": "苹果公司", "target": "美国", "relation": "位于"},
                {"source": "苹果公司", "target": "科技公司", "relation": "属于"}
            ],
            "nodes_count": 4,
            "edges_count": 3
        }
        tasks_storage[task_id] = task
        
    except Exception as e:
        task.status = "failed"
        task.result = {"error": str(e)}
        tasks_storage[task_id] = task

@app.get("/api/knowledge-graph/{task_id}")
async def get_knowledge_graph(task_id: str):
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")
    
    return task.result

@app.get("/api/visualization/{task_id}")
async def get_visualization(task_id: str):
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")
    
    # 创建一个简单的知识图谱可视化
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        import networkx as nx
        from io import BytesIO
        import base64
        
        # 创建图谱
        G = nx.Graph()
        
        # 添加节点和边
        entities = task.result.get("entities", [])
        relations = task.result.get("relations", [])
        
        for entity in entities:
            G.add_node(entity)
        
        for relation in relations:
            G.add_edge(relation["source"], relation["target"], 
                      relation=relation["relation"])
        
        # 设置中文字体
        import matplotlib
        matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        # 创建图像
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                              node_size=3000, alpha=0.7)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, alpha=0.5, width=2)
        
        # 绘制标签
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # 绘制边标签
        edge_labels = nx.get_edge_attributes(G, 'relation')
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
        
        plt.title(f"Knowledge Graph Visualization\nEntities: {len(entities)}, Relations: {len(relations)}", 
                 fontsize=14, pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # 保存到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(img_buffer, media_type="image/png")
        
    except Exception as e:
        print(f"可视化生成失败: {e}")
        raise HTTPException(status_code=500, detail="可视化生成失败")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)