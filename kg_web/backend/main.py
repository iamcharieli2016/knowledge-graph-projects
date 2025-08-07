#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱构建Web API服务
"""

import sys
import os
from pathlib import Path

# 添加kg_core到Python路径
kg_core_path = Path(__file__).parent.parent.parent / "kg_core"
sys.path.insert(0, str(kg_core_path))

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import uuid
from datetime import datetime
import logging

from kg_core.main import KnowledgeGraphDemo
from kg_core.utils.config import Config
from kg_core.data.sample_data import SampleDataGenerator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="知识图谱构建系统",
    description="基于Web的知识图谱构建和管理平台",
    version="1.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局变量
tasks: Dict[str, Dict] = {}
kg_core_instance = None
current_config = None


class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfigModel(BaseModel):
    """配置模型"""
    extraction: Dict[str, Any]
    mapping: Dict[str, Any]
    fusion: Dict[str, Any]
    visualization: Dict[str, Any]
    output_dir: str = "output"
    log_level: str = "INFO"


class TextInput(BaseModel):
    """文本输入模型"""
    texts: List[str]
    domain: Optional[str] = None


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str
    status: str
    message: str
    created_at: str


class KnowledgeGraphResponse(BaseModel):
    """知识图谱响应模型"""
    entities: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]
    statistics: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    global current_config
    current_config = Config()
    logger.info("知识图谱构建API服务启动")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "知识图谱构建API服务", "version": "1.0.0"}


@app.get("/api/config")
async def get_config():
    """获取当前配置"""
    return {
        "extraction": {
            "similarity_threshold": current_config.extraction.similarity_threshold,
            "min_entity_length": current_config.extraction.min_entity_length,
            "min_confidence": current_config.extraction.min_confidence,
            "max_context_window": current_config.extraction.max_context_window,
            "use_patterns": current_config.extraction.use_patterns,
            "use_pos_tagging": current_config.extraction.use_pos_tagging,
            "use_dictionary": current_config.extraction.use_dictionary
        },
        "mapping": {
            "entity_similarity_threshold": current_config.mapping.entity_similarity_threshold,
            "relation_similarity_threshold": current_config.mapping.relation_similarity_threshold,
            "fuzzy_match_threshold": current_config.mapping.fuzzy_match_threshold,
            "use_semantic_mapping": current_config.mapping.use_semantic_mapping,
            "use_context_mapping": current_config.mapping.use_context_mapping
        },
        "fusion": {
            "entity_fusion_threshold": current_config.fusion.entity_fusion_threshold,
            "relation_fusion_threshold": current_config.fusion.relation_fusion_threshold,
            "conflict_resolution_strategy": current_config.fusion.conflict_resolution_strategy,
            "merge_similar_entities": current_config.fusion.merge_similar_entities,
            "preserve_provenance": current_config.fusion.preserve_provenance
        },
        "visualization": {
            "max_nodes": current_config.visualization.max_nodes,
            "node_size": current_config.visualization.node_size,
            "edge_width": current_config.visualization.edge_width,
            "layout": current_config.visualization.layout,
            "output_format": current_config.visualization.output_format,
            "figure_size": current_config.visualization.figure_size
        },
        "output_dir": current_config.output_dir,
        "log_level": current_config.log_level
    }


@app.post("/api/config")
async def update_config(config: ConfigModel):
    """更新配置"""
    try:
        global current_config
        
        # 更新配置
        current_config.update_extraction_config(**config.extraction)
        current_config.update_mapping_config(**config.mapping)
        current_config.update_fusion_config(**config.fusion)
        current_config.update_visualization_config(**config.visualization)
        
        current_config.output_dir = config.output_dir
        current_config.log_level = config.log_level
        
        # 保存配置
        current_config.save_config()
        
        return {"status": "success", "message": "配置更新成功"}
    
    except Exception as e:
        logger.error(f"配置更新失败: {e}")
        raise HTTPException(status_code=400, detail=f"配置更新失败: {e}")


@app.get("/api/sample-data")
async def get_sample_data():
    """获取示例数据"""
    try:
        sample_generator = SampleDataGenerator()
        texts = sample_generator.get_sample_texts()
        
        return {
            "texts": texts[:5],  # 返回前5个示例
            "domains": ["technology", "academic", "business"],
            "total_count": len(texts)
        }
    
    except Exception as e:
        logger.error(f"获取示例数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取示例数据失败: {e}")


@app.post("/api/tasks/create")
async def create_kg_task(text_input: TextInput, background_tasks: BackgroundTasks):
    """创建知识图谱构建任务"""
    try:
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        tasks[task_id] = {
            "id": task_id,
            "status": TaskStatus.PENDING,
            "message": "任务已创建，等待处理",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "results": None,
            "error": None
        }
        
        # 启动后台任务
        background_tasks.add_task(run_kg_construction, task_id, text_input.texts)
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="任务已创建，开始处理",
            created_at=tasks[task_id]["created_at"]
        )
    
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {e}")


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return tasks[task_id]


@app.get("/api/tasks")
async def get_all_tasks():
    """获取所有任务"""
    return {"tasks": list(tasks.values())}


@app.get("/api/knowledge-graph/{task_id}")
async def get_knowledge_graph(task_id: str):
    """获取知识图谱数据"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    if task["status"] != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="任务未完成")
    
    if not task["results"]:
        raise HTTPException(status_code=404, detail="知识图谱数据不存在")
    
    return task["results"]


@app.get("/api/visualization/{task_id}")
async def get_visualization(task_id: str):
    """获取可视化图像"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查可视化文件是否存在
    viz_file = f"static/visualizations/{task_id}.png"
    if not os.path.exists(viz_file):
        raise HTTPException(status_code=404, detail="可视化图像不存在")
    
    return FileResponse(viz_file, media_type="image/png")


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 删除任务记录
    del tasks[task_id]
    
    # 删除相关文件
    viz_file = f"static/visualizations/{task_id}.png"
    if os.path.exists(viz_file):
        os.remove(viz_file)
    
    return {"status": "success", "message": "任务已删除"}


async def run_kg_construction(task_id: str, texts: List[str]):
    """运行知识图谱构建任务"""
    try:
        # 更新任务状态
        tasks[task_id]["status"] = TaskStatus.RUNNING
        tasks[task_id]["message"] = "正在构建知识图谱..."
        tasks[task_id]["progress"] = 10
        
        # 创建KG演示实例
        demo = KnowledgeGraphDemo()
        
        # 步骤1: 主体定义
        tasks[task_id]["message"] = "步骤1: 主体定义"
        tasks[task_id]["progress"] = 20
        demo.step1_ontology_definition()
        
        # 步骤2: 知识抽取 (使用提供的文本)
        tasks[task_id]["message"] = "步骤2: 知识抽取"
        tasks[task_id]["progress"] = 40
        
        # 使用用户提供的文本进行知识抽取
        extracted_entities, extracted_relations = demo.step2_knowledge_extraction(custom_texts=texts)
        
        # 步骤3: 知识映射
        tasks[task_id]["message"] = "步骤3: 知识映射"
        tasks[task_id]["progress"] = 60
        entity_mappings, relation_mappings = demo.step3_knowledge_mapping(
            extracted_entities, extracted_relations
        )
        
        # 步骤4: 知识融合
        tasks[task_id]["message"] = "步骤4: 知识融合"
        tasks[task_id]["progress"] = 80
        entity_fusion_results, relation_fusion_results = demo.step4_knowledge_fusion(
            entity_mappings, relation_mappings
        )
        
        # 构建最终知识图谱
        tasks[task_id]["message"] = "构建最终知识图谱"
        tasks[task_id]["progress"] = 90
        final_kg = demo.build_final_knowledge_graph(
            entity_fusion_results, relation_fusion_results
        )
        
        # 生成可视化
        tasks[task_id]["message"] = "生成可视化"
        tasks[task_id]["progress"] = 95
        
        # 确保静态目录存在
        os.makedirs("static/visualizations", exist_ok=True)
        viz_file = f"static/visualizations/{task_id}.png"
        
        final_kg.visualize(output_file=viz_file, max_nodes=50)
        
        # 准备结果数据
        entities_data = []
        for entity in final_kg.entities.values():
            entities_data.append({
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "properties": entity.properties or {},
                "aliases": entity.aliases or []
            })
        
        relations_data = []
        for relation in final_kg.relations.values():
            relations_data.append({
                "id": relation.id,
                "type": relation.type,
                "source": relation.head_entity_id,
                "target": relation.tail_entity_id,
                "properties": relation.properties or {},
                "confidence": relation.confidence
            })
        
        stats = final_kg.get_statistics()
        
        # 保存结果
        tasks[task_id]["status"] = TaskStatus.COMPLETED
        tasks[task_id]["message"] = "知识图谱构建完成"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["results"] = {
            "entities": entities_data,
            "relations": relations_data,
            "statistics": {
                "entity_count": stats.entity_count,
                "relation_count": stats.relation_count,
                "entity_types": stats.entity_types,
                "relation_types": stats.relation_types,
                "avg_degree": stats.avg_degree,
                "connected_components": stats.connected_components,
                "density": stats.density
            }
        }
        
        logger.info(f"任务 {task_id} 完成")
        
    except Exception as e:
        logger.error(f"任务 {task_id} 失败: {e}")
        tasks[task_id]["status"] = TaskStatus.FAILED
        tasks[task_id]["message"] = f"任务失败: {str(e)}"
        tasks[task_id]["error"] = str(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)