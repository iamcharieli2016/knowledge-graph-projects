#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可视化功能脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_core.entity_definition.entity_types import Entity
from kg_core.entity_definition.relation_types import Relation
from kg_core.knowledge_fusion.knowledge_graph import KnowledgeGraph
from kg_core.entity_definition.ontology import Ontology


def test_visualization():
    """测试可视化功能"""
    print("🧪 测试知识图谱可视化...")
    
    # 创建知识图谱
    ontology = Ontology()
    kg = KnowledgeGraph(ontology)
    
    # 添加测试实体
    test_entities = [
        Entity("person_1", "张三", "Person", {"occupation": "教授"}, ["Professor Zhang"]),
        Entity("person_2", "李四", "Person", {"occupation": "工程师"}, ["Engineer Li"]),
        Entity("org_1", "北京大学", "Organization", {"type": "大学"}, ["PKU", "Peking University"]),
        Entity("org_2", "腾讯公司", "Organization", {"type": "公司"}, ["Tencent"]),
        Entity("loc_1", "北京市", "Location", {"type": "城市"}, ["Beijing"]),
        Entity("prod_1", "微信", "Product", {"type": "软件"}, ["WeChat"])
    ]
    
    for entity in test_entities:
        kg.add_entity(entity)
    
    # 添加测试关系
    test_relations = [
        Relation("rel_1", "works_for", "person_1", "org_1", {"source": "test"}, 1.0),
        Relation("rel_2", "works_for", "person_2", "org_2", {"source": "test"}, 1.0),
        Relation("rel_3", "located_in", "org_1", "loc_1", {"source": "test"}, 1.0),
        Relation("rel_4", "located_in", "org_2", "loc_1", {"source": "test"}, 1.0),
        Relation("rel_5", "produces", "org_2", "prod_1", {"source": "test"}, 1.0)
    ]
    
    for relation in test_relations:
        kg.add_relation(relation)
    
    # 生成可视化
    output_file = "output/test_visualization.png"
    
    print(f"📊 生成可视化图像: {output_file}")
    try:
        kg.visualize(output_file=output_file, max_nodes=20)
        print("✅ 可视化测试成功！")
        
        # 检查文件是否生成
        if os.path.exists(output_file):
            print(f"✅ 图像文件已生成: {output_file}")
        else:
            print("❌ 图像文件未生成")
            
    except Exception as e:
        print(f"❌ 可视化测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 打印统计信息
    kg.print_summary()


def test_font_manager():
    """测试字体管理器"""
    print("\n🔤 测试字体管理器...")
    
    from kg_core.utils.visualization import font_manager, get_display_text, create_title
    
    print(f"可用字体: {font_manager.available_font}")
    print(f"字体配置状态: {font_manager.font_configured}")
    
    # 测试文本转换
    test_texts = [
        "张三",
        "北京大学", 
        "腾讯公司",
        "知识图谱可视化",
        "Hello World"
    ]
    
    print("\n文本转换测试:")
    for text in test_texts:
        display_text = get_display_text(text)
        print(f"  {text} -> {display_text}")
    
    # 测试标题生成
    title = create_title(10, 15)
    print(f"\n标题: {title}")


if __name__ == "__main__":
    test_font_manager()
    test_visualization()