#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的知识图谱构建流程测试脚本
"""

import requests
import json
import time
import os

# 清除代理设置
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoints():
    """测试所有API端点"""
    print("🔍 开始测试API端点...")
    
    # 测试根路径
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print(f"✅ 根路径: {response.json()}")
    else:
        print(f"❌ 根路径失败: {response.status_code} - {response.text}")
        return None
    
    # 测试配置获取
    response = requests.get(f"{BASE_URL}/api/config")
    if response.status_code == 200:
        print(f"✅ 获取配置: {response.json()}")
    else:
        print(f"❌ 配置获取失败: {response.status_code} - {response.text}")
        return None
    
    # 测试示例数据获取
    response = requests.get(f"{BASE_URL}/api/sample-data")
    if response.status_code == 200:
        sample_data = response.json()
        print(f"✅ 示例数据: {len(sample_data['texts'])} 条文本")
        return sample_data
    else:
        print(f"❌ 示例数据获取失败: {response.status_code} - {response.text}")
        return None

def test_knowledge_graph_construction(text):
    """测试知识图谱构建流程"""
    print(f"\n🚀 开始构建知识图谱...")
    print(f"📝 输入文本: {text[:50]}...")
    
    # 创建任务
    task_data = {"text": text}
    response = requests.post(f"{BASE_URL}/api/tasks/create", json=task_data)
    task_info = response.json()
    task_id = task_info["task_id"]
    print(f"✅ 任务创建成功: {task_id}")
    
    # 监控任务进度
    print("📊 监控任务进度:")
    while True:
        response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
        task = response.json()
        status = task["status"]
        progress = task["progress"]
        
        print(f"   状态: {status} | 进度: {progress}%")
        
        if status == "completed":
            print("✅ 任务完成!")
            break
        elif status == "failed":
            print("❌ 任务失败!")
            return None
        
        time.sleep(2)
    
    # 获取知识图谱数据
    response = requests.get(f"{BASE_URL}/api/knowledge-graph/{task_id}")
    kg_data = response.json()
    
    print(f"\n📈 知识图谱结果:")
    print(f"   实体数量: {kg_data['nodes_count']}")
    print(f"   关系数量: {kg_data['edges_count']}")
    print(f"   实体: {kg_data['entities']}")
    print(f"   关系:")
    for relation in kg_data['relations']:
        print(f"     {relation['source']} --{relation['relation']}--> {relation['target']}")
    
    return task_id, kg_data

def test_configuration_update():
    """测试配置更新"""
    print(f"\n⚙️  测试配置更新...")
    
    new_config = {
        "max_entities": 100,
        "similarity_threshold": 0.8,
        "extraction_method": "hybrid",
        "language": "zh"
    }
    
    response = requests.post(f"{BASE_URL}/api/config", json=new_config)
    print(f"✅ 配置更新: {response.json()}")
    
    # 验证配置是否更新
    response = requests.get(f"{BASE_URL}/api/config")
    updated_config = response.json()
    print(f"✅ 验证配置: {updated_config}")

def main():
    """主测试流程"""
    print("🎯 知识图谱构建系统 - 完整流程测试")
    print("=" * 50)
    
    try:
        # 测试API端点
        sample_data = test_api_endpoints()
        
        # 测试配置更新
        test_configuration_update()
        
        # 使用示例数据测试知识图谱构建
        for i, text in enumerate(sample_data['texts'][:2]):  # 测试前两个示例
            print(f"\n🔄 测试样本 {i+1}:")
            task_id, kg_data = test_knowledge_graph_construction(text)
            if kg_data:
                print(f"✅ 样本 {i+1} 处理成功")
            else:
                print(f"❌ 样本 {i+1} 处理失败")
        
        # 列出所有任务
        print(f"\n📋 所有任务列表:")
        response = requests.get(f"{BASE_URL}/api/tasks")
        tasks = response.json()
        for task in tasks:
            print(f"   {task['id'][:8]}... | {task['status']} | {task['progress']}%")
        
        print(f"\n🎉 所有测试完成!")
        print(f"📱 前端地址: http://localhost:3002")
        print(f"🔗 后端地址: http://localhost:8000")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务已启动")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()