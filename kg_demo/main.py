#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱构建Demo主程序

演示知识图谱构建的四个主要步骤：
1. 主体定义 (Entity Definition)
2. 知识抽取 (Knowledge Extraction) 
3. 知识映射 (Knowledge Mapping)
4. 知识融合 (Knowledge Fusion)
"""

import os
import sys
import argparse
from typing import List, Dict

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_demo.entity_definition.ontology import Ontology
from kg_demo.entity_definition.entity_types import Entity, EntityTypes
from kg_demo.entity_definition.relation_types import Relation, RelationTypes

from kg_demo.knowledge_extraction.text_extractor import TextExtractor
from kg_demo.knowledge_extraction.entity_extractor import EntityExtractor
from kg_demo.knowledge_extraction.relation_extractor import RelationExtractor
from kg_demo.knowledge_extraction.pattern_extractor import PatternExtractor

from kg_demo.knowledge_mapping.entity_mapper import EntityMapper
from kg_demo.knowledge_mapping.relation_mapper import RelationMapper
from kg_demo.knowledge_mapping.ontology_mapper import OntologyMapper
from kg_demo.knowledge_mapping.similarity_calculator import SimilarityCalculator

from kg_demo.knowledge_fusion.entity_fusion import EntityFusion
from kg_demo.knowledge_fusion.relation_fusion import RelationFusion
from kg_demo.knowledge_fusion.conflict_resolution import ConflictResolver
from kg_demo.knowledge_fusion.knowledge_graph import KnowledgeGraph

from kg_demo.data.sample_data import SampleDataGenerator


class KnowledgeGraphDemo:
    """知识图谱构建演示"""
    
    def __init__(self):
        print("🚀 初始化知识图谱构建演示系统...")
        self.ontology = Ontology()
        self.knowledge_graph = KnowledgeGraph(self.ontology)
        self.sample_data = SampleDataGenerator()
        
        # 初始化各个模块
        self.text_extractor = TextExtractor()
        self.entity_extractor = EntityExtractor()
        self.relation_extractor = RelationExtractor()
        self.pattern_extractor = PatternExtractor()
        
        self.entity_mapper = EntityMapper()
        self.relation_mapper = RelationMapper(self.ontology)
        self.ontology_mapper = OntologyMapper(self.ontology)
        
        self.entity_fusion = EntityFusion()
        self.relation_fusion = RelationFusion()
        self.conflict_resolver = ConflictResolver()
        
        print("✅ 系统初始化完成!\n")
    
    def step1_ontology_definition(self):
        """步骤1: 主体定义"""
        print("=" * 60)
        print("📋 步骤1: 主体定义 (Ontology Definition)")
        print("=" * 60)
        
        print("🔧 构建知识图谱本体结构...")
        
        # 显示默认本体
        self.ontology.print_ontology_summary()
        
        # 导出本体
        ontology_file = "kg_demo/data/ontology.json"
        self.ontology.export_ontology(ontology_file)
        print(f"📁 本体已导出到: {ontology_file}")
        
        print("✅ 主体定义完成!\n")
        return True
    
    def step2_knowledge_extraction(self):
        """步骤2: 知识抽取"""
        print("=" * 60)
        print("🔍 步骤2: 知识抽取 (Knowledge Extraction)")
        print("=" * 60)
        
        # 获取示例文本
        sample_texts = self.sample_data.get_sample_texts()
        print(f"📄 处理 {len(sample_texts)} 个示例文本...")
        
        all_extracted_entities = []
        all_extracted_relations = []
        
        for i, text in enumerate(sample_texts):
            print(f"\n🔎 处理文本 {i+1}: {text[:50]}...")
            
            # 文本预处理
            processed_text = self.text_extractor.preprocess_text(text)
            keywords = self.text_extractor.extract_keywords(processed_text)
            print(f"   关键词: {keywords[:5]}")
            
            # 实体抽取
            extracted_entities = self.entity_extractor.extract_entities(processed_text)
            print(f"   抽取实体: {len(extracted_entities)} 个")
            
            # 关系抽取
            extracted_relations = self.relation_extractor.extract_relations(
                processed_text, extracted_entities
            )
            print(f"   抽取关系: {len(extracted_relations)} 个")
            
            all_extracted_entities.extend(extracted_entities)
            all_extracted_relations.extend(extracted_relations)
        
        # 打印抽取统计
        print(f"\n📊 知识抽取统计:")
        print(f"   总实体数: {len(all_extracted_entities)}")
        print(f"   总关系数: {len(all_extracted_relations)}")
        
        # 显示部分抽取结果
        print(f"\n🎯 实体抽取示例:")
        for entity in all_extracted_entities[:5]:
            print(f"   - {entity.text} ({entity.type}) - 置信度: {entity.confidence:.2f}")
        
        print(f"\n🔗 关系抽取示例:")
        for relation in all_extracted_relations[:5]:
            print(f"   - {relation.head_entity} -[{relation.relation_type}]-> {relation.tail_entity}")
        
        print("✅ 知识抽取完成!\n")
        return all_extracted_entities, all_extracted_relations
    
    def step3_knowledge_mapping(self, extracted_entities, extracted_relations):
        """步骤3: 知识映射"""
        print("=" * 60)
        print("🗺️  步骤3: 知识映射 (Knowledge Mapping)")
        print("=" * 60)
        
        print("🔄 进行实体映射...")
        
        # 添加一些已知实体到映射器
        sample_entities = self.sample_data.get_sample_entities()
        for entity in sample_entities:
            self.entity_mapper.add_known_entity(entity)
        
        # 实体映射
        entity_mappings = self.entity_mapper.batch_map_entities(extracted_entities)
        print(f"   映射结果: {len(entity_mappings)} 个实体")
        
        # 打印映射统计
        self.entity_mapper.print_mapping_results(entity_mappings)
        
        print("\n🔄 进行关系映射...")
        
        # 构建实体类型映射
        entity_type_mapping = {}
        for mapping in entity_mappings:
            if mapping.mapped_entity:
                entity_type_mapping[mapping.extracted_entity.text] = mapping.mapped_entity.type
            else:
                entity_type_mapping[mapping.extracted_entity.text] = mapping.extracted_entity.type
        
        # 关系映射
        relation_mappings = self.relation_mapper.batch_map_relations(
            extracted_relations, entity_type_mapping
        )
        print(f"   映射结果: {len(relation_mappings)} 个关系")
        
        # 打印关系映射统计
        self.relation_mapper.print_mapping_results(relation_mappings)
        
        print("✅ 知识映射完成!\n")
        return entity_mappings, relation_mappings
    
    def step4_knowledge_fusion(self, entity_mappings, relation_mappings):
        """步骤4: 知识融合"""
        print("=" * 60)
        print("🔄 步骤4: 知识融合 (Knowledge Fusion)")
        print("=" * 60)
        
        print("🔗 准备融合数据...")
        
        # 准备实体数据
        entities_to_fuse = []
        for mapping in entity_mappings:
            if mapping.mapped_entity:
                entities_to_fuse.append(mapping.mapped_entity)
            else:
                # 创建新实体
                new_entity = self.entity_mapper.create_new_entity(
                    mapping.extracted_entity
                )
                entities_to_fuse.append(new_entity)
        
        # 准备关系数据
        relations_to_fuse = []
        entity_id_map = {entity.name: entity.id for entity in entities_to_fuse}
        
        for mapping in relation_mappings:
            if mapping.mapped_relation_type and mapping.validation_result:
                # 获取实体ID
                head_id = entity_id_map.get(mapping.extracted_relation.head_entity)
                tail_id = entity_id_map.get(mapping.extracted_relation.tail_entity)
                
                if head_id and tail_id:
                    relation = Relation(
                        id=f"rel_{len(relations_to_fuse)}",
                        type=mapping.mapped_relation_type,
                        head_entity_id=head_id,
                        tail_entity_id=tail_id,
                        properties={
                            'context': mapping.extracted_relation.context,
                            'source': 'extraction'
                        },
                        confidence=mapping.confidence
                    )
                    relations_to_fuse.append(relation)
        
        print(f"   准备融合 {len(entities_to_fuse)} 个实体")
        print(f"   准备融合 {len(relations_to_fuse)} 个关系")
        
        print("\n🔄 进行实体融合...")
        entity_fusion_results = self.entity_fusion.batch_fuse_entities(entities_to_fuse)
        self.entity_fusion.print_fusion_results(entity_fusion_results)
        
        print("\n🔄 进行关系融合...")
        relation_fusion_results = self.relation_fusion.batch_fuse_relations(relations_to_fuse)
        self.relation_fusion.print_fusion_results(relation_fusion_results)
        
        print("\n🔍 检测和解决冲突...")
        all_entities = [result.fused_entity for result in entity_fusion_results]
        all_relations = [result.fused_relation for result in relation_fusion_results]
        
        entity_conflicts = self.conflict_resolver.detect_entity_conflicts(all_entities)
        relation_conflicts = self.conflict_resolver.detect_relation_conflicts(all_relations)
        
        all_conflicts = entity_conflicts + relation_conflicts
        print(f"   发现 {len(all_conflicts)} 个冲突")
        
        if all_conflicts:
            resolved_conflicts = self.conflict_resolver.batch_resolve_conflicts(all_conflicts)
            self.conflict_resolver.print_conflict_summary(resolved_conflicts)
        
        print("✅ 知识融合完成!\n")
        return entity_fusion_results, relation_fusion_results
    
    def build_final_knowledge_graph(self, entity_fusion_results, relation_fusion_results):
        """构建最终知识图谱"""
        print("=" * 60)
        print("🏗️  构建最终知识图谱")
        print("=" * 60)
        
        print("📦 添加融合后的实体和关系...")
        
        # 添加实体
        for result in entity_fusion_results:
            self.knowledge_graph.add_entity(result.fused_entity)
        
        # 添加关系
        successful_relations = 0
        for result in relation_fusion_results:
            try:
                self.knowledge_graph.add_relation(result.fused_relation)
                successful_relations += 1
            except ValueError as e:
                print(f"⚠️  跳过无效关系: {e}")
                continue
        
        print(f"✅ 成功添加 {len(entity_fusion_results)} 个实体")
        print(f"✅ 成功添加 {successful_relations} 个关系")
        
        # 验证知识图谱
        print(f"\n🔍 验证知识图谱...")
        validation_results = self.knowledge_graph.validate_knowledge_graph()
        
        if validation_results['valid']:
            print("✅ 知识图谱验证通过!")
        else:
            print("⚠️  知识图谱验证发现问题:")
            for issue in validation_results['issues']:
                print(f"   - {issue}")
        
        # 打印知识图谱摘要
        print(f"\n📊 最终知识图谱统计:")
        self.knowledge_graph.print_summary()
        
        return self.knowledge_graph
    
    def export_results(self, knowledge_graph):
        """导出结果"""
        print("=" * 60)
        print("💾 导出结果")
        print("=" * 60)
        
        # 创建输出目录
        output_dir = "kg_demo/output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 导出JSON格式
        json_file = f"{output_dir}/knowledge_graph.json"
        knowledge_graph.export_to_json(json_file)
        print(f"📁 JSON格式已导出到: {json_file}")
        
        # 导出CSV格式
        entities_csv = f"{output_dir}/entities.csv"
        relations_csv = f"{output_dir}/relations.csv"
        knowledge_graph.export_to_csv(entities_csv, relations_csv)
        print(f"📁 CSV格式已导出到: {entities_csv}, {relations_csv}")
        
        # 生成可视化
        try:
            viz_file = f"{output_dir}/knowledge_graph_visualization.png"
            knowledge_graph.visualize(output_file=viz_file, max_nodes=30)
            print(f"📁 可视化图已保存到: {viz_file}")
        except Exception as e:
            print(f"⚠️  可视化生成失败: {e}")
        
        print("✅ 结果导出完成!\n")
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("🎯 开始知识图谱构建完整演示")
        print("=" * 80)
        
        try:
            # 步骤1: 主体定义
            self.step1_ontology_definition()
            
            # 步骤2: 知识抽取
            extracted_entities, extracted_relations = self.step2_knowledge_extraction()
            
            # 步骤3: 知识映射
            entity_mappings, relation_mappings = self.step3_knowledge_mapping(
                extracted_entities, extracted_relations
            )
            
            # 步骤4: 知识融合
            entity_fusion_results, relation_fusion_results = self.step4_knowledge_fusion(
                entity_mappings, relation_mappings
            )
            
            # 构建最终知识图谱
            final_kg = self.build_final_knowledge_graph(
                entity_fusion_results, relation_fusion_results
            )
            
            # 导出结果
            self.export_results(final_kg)
            
            print("🎉 知识图谱构建演示完成!")
            print("=" * 80)
            
            return final_kg
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_interactive_demo(self):
        """运行交互式演示"""
        print("🎮 交互式知识图谱构建演示")
        print("=" * 60)
        
        while True:
            print("\n请选择要执行的步骤:")
            print("1. 主体定义")
            print("2. 知识抽取") 
            print("3. 知识映射")
            print("4. 知识融合")
            print("5. 完整演示")
            print("6. 查看当前图谱")
            print("0. 退出")
            
            choice = input("\n请输入选择 (0-6): ").strip()
            
            if choice == '0':
                print("👋 感谢使用知识图谱构建演示系统!")
                break
            elif choice == '1':
                self.step1_ontology_definition()
            elif choice == '2':
                extracted_entities, extracted_relations = self.step2_knowledge_extraction()
                self.extracted_entities = extracted_entities
                self.extracted_relations = extracted_relations
            elif choice == '3':
                if hasattr(self, 'extracted_entities') and hasattr(self, 'extracted_relations'):
                    entity_mappings, relation_mappings = self.step3_knowledge_mapping(
                        self.extracted_entities, self.extracted_relations
                    )
                    self.entity_mappings = entity_mappings
                    self.relation_mappings = relation_mappings
                else:
                    print("⚠️  请先执行知识抽取步骤!")
            elif choice == '4':
                if hasattr(self, 'entity_mappings') and hasattr(self, 'relation_mappings'):
                    entity_fusion_results, relation_fusion_results = self.step4_knowledge_fusion(
                        self.entity_mappings, self.relation_mappings
                    )
                    final_kg = self.build_final_knowledge_graph(
                        entity_fusion_results, relation_fusion_results
                    )
                    self.export_results(final_kg)
                else:
                    print("⚠️  请先执行知识映射步骤!")
            elif choice == '5':
                self.run_complete_demo()
            elif choice == '6':
                self.knowledge_graph.print_summary()
            else:
                print("❌ 无效选择，请重新输入!")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='知识图谱构建演示系统')
    parser.add_argument('--mode', choices=['complete', 'interactive'], 
                       default='complete', help='运行模式')
    parser.add_argument('--step', type=int, choices=[1, 2, 3, 4], 
                       help='只运行指定步骤')
    
    args = parser.parse_args()
    
    # 创建演示实例
    demo = KnowledgeGraphDemo()
    
    if args.step:
        # 运行指定步骤
        if args.step == 1:
            demo.step1_ontology_definition()
        elif args.step == 2:
            demo.step2_knowledge_extraction()
        elif args.step == 3:
            print("⚠️  单独运行步骤3需要先执行步骤2的结果")
        elif args.step == 4:
            print("⚠️  单独运行步骤4需要先执行步骤2和3的结果")
    elif args.mode == 'interactive':
        demo.run_interactive_demo()
    else:
        demo.run_complete_demo()


if __name__ == "__main__":
    main()