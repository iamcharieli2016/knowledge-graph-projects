"""
知识图谱模块 - 构建和管理完整的知识图谱
"""
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import uuid
import pandas as pd

from ..entity_definition.entity_types import Entity
from ..entity_definition.relation_types import Relation
from ..entity_definition.ontology import Ontology
from .entity_fusion import EntityFusion, FusionResult
from .relation_fusion import RelationFusion, RelationFusionResult
from .conflict_resolution import ConflictResolver, Conflict


@dataclass
class KnowledgeGraphStats:
    """知识图谱统计信息"""
    entity_count: int
    relation_count: int
    entity_types: Dict[str, int]
    relation_types: Dict[str, int]
    avg_degree: float
    connected_components: int
    density: float


class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self, ontology: Ontology = None):
        self.ontology = ontology or Ontology()
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.graph = nx.MultiDiGraph()  # 支持多重有向图
        
        # 融合器
        self.entity_fusion = EntityFusion()
        self.relation_fusion = RelationFusion()
        self.conflict_resolver = ConflictResolver()
        
        # 索引
        self.entity_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.relation_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.entity_name_index: Dict[str, str] = {}
    
    def add_entity(self, entity: Entity):
        """添加实体"""
        self.entities[entity.id] = entity
        self.graph.add_node(entity.id, 
                           name=entity.name,
                           type=entity.type,
                           properties=entity.properties or {})
        
        # 更新索引
        self.entity_type_index[entity.type].add(entity.id)
        self.entity_name_index[entity.name] = entity.id
        
        # 添加别名索引
        if entity.aliases:
            for alias in entity.aliases:
                self.entity_name_index[alias] = entity.id
    
    def add_relation(self, relation: Relation):
        """添加关系"""
        self.relations[relation.id] = relation
        
        # 检查实体是否存在
        if (relation.head_entity_id not in self.entities or 
            relation.tail_entity_id not in self.entities):
            raise ValueError(f"关系 {relation.id} 的实体不存在")
        
        self.graph.add_edge(relation.head_entity_id, 
                           relation.tail_entity_id,
                           relation_id=relation.id,
                           relation_type=relation.type,
                           properties=relation.properties or {},
                           confidence=relation.confidence)
        
        # 更新索引 
        self.relation_type_index[relation.type].add(relation.id)
    
    def batch_add_entities(self, entities: List[Entity]):
        """批量添加实体"""
        for entity in entities:
            self.add_entity(entity)
    
    def batch_add_relations(self, relations: List[Relation]):
        """批量添加关系"""
        for relation in relations:
            try:
                self.add_relation(relation)
            except ValueError as e:
                print(f"警告: {e}")
                continue
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        return self.entities.get(entity_id)
    
    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """根据名称获取实体"""
        entity_id = self.entity_name_index.get(name)
        return self.entities.get(entity_id) if entity_id else None
    
    def get_relation(self, relation_id: str) -> Optional[Relation]:
        """获取关系"""
        return self.relations.get(relation_id)
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """获取指定类型的实体"""
        entity_ids = self.entity_type_index.get(entity_type, set())
        return [self.entities[eid] for eid in entity_ids]
    
    def get_relations_by_type(self, relation_type: str) -> List[Relation]:
        """获取指定类型的关系"""
        relation_ids = self.relation_type_index.get(relation_type, set())
        return [self.relations[rid] for rid in relation_ids]
    
    def get_neighbors(self, entity_id: str, relation_type: str = None) -> List[str]:
        """获取邻居实体"""
        neighbors = []
        
        if entity_id not in self.graph:
            return neighbors
        
        # 出边邻居
        for neighbor in self.graph.successors(entity_id):
            edge_data = self.graph.get_edge_data(entity_id, neighbor)
            for edge_key, edge_attrs in edge_data.items():
                if relation_type is None or edge_attrs.get('relation_type') == relation_type:
                    neighbors.append(neighbor)
                    break
        
        # 入边邻居
        for neighbor in self.graph.predecessors(entity_id):
            edge_data = self.graph.get_edge_data(neighbor, entity_id)
            for edge_key, edge_attrs in edge_data.items():
                if relation_type is None or edge_attrs.get('relation_type') == relation_type:
                    neighbors.append(neighbor)
                    break
        
        return list(set(neighbors))  # 去重
    
    def find_path(self, start_entity_id: str, end_entity_id: str, 
                  max_length: int = 3) -> List[List[str]]:
        """找到两个实体之间的路径"""
        try:
            # 使用NetworkX找到所有简单路径
            paths = list(nx.all_simple_paths(self.graph.to_undirected(), 
                                           start_entity_id, end_entity_id,
                                           cutoff=max_length))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def query_subgraph(self, entity_ids: List[str], depth: int = 1) -> 'KnowledgeGraph':
        """查询子图"""
        subgraph_entities = set(entity_ids)
        
        # 扩展到指定深度
        for _ in range(depth):
            new_entities = set()
            for entity_id in subgraph_entities:
                neighbors = self.get_neighbors(entity_id)
                new_entities.update(neighbors)
            subgraph_entities.update(new_entities)
        
        # 创建子图
        subgraph = KnowledgeGraph(self.ontology)
        
        # 添加实体
        for entity_id in subgraph_entities:
            if entity_id in self.entities:
                subgraph.add_entity(self.entities[entity_id])
        
        # 添加关系
        for relation in self.relations.values():
            if (relation.head_entity_id in subgraph_entities and
                relation.tail_entity_id in subgraph_entities):
                subgraph.add_relation(relation)
        
        return subgraph
    
    def merge_knowledge_graph(self, other_kg: 'KnowledgeGraph'):
        """合并另一个知识图谱"""
        # 融合实体
        all_entities = list(self.entities.values()) + list(other_kg.entities.values())
        entity_fusion_results = self.entity_fusion.batch_fuse_entities(all_entities)
        
        # 清空当前实体
        self.entities.clear()
        self.entity_type_index.clear()
        self.entity_name_index.clear()
        
        # 添加融合后的实体
        entity_id_mapping = {}  # 旧ID到新ID的映射
        for result in entity_fusion_results:
            fused_entity = result.fused_entity
            self.add_entity(fused_entity)
            
            # 记录ID映射
            for source_entity in result.source_entities:
                entity_id_mapping[source_entity.id] = fused_entity.id
        
        # 更新关系的实体ID
        all_relations = list(self.relations.values()) + list(other_kg.relations.values())
        updated_relations = []
        
        for relation in all_relations:
            new_head_id = entity_id_mapping.get(relation.head_entity_id, relation.head_entity_id)
            new_tail_id = entity_id_mapping.get(relation.tail_entity_id, relation.tail_entity_id)
            
            if new_head_id in self.entities and new_tail_id in self.entities:
                updated_relation = Relation(
                    id=relation.id,
                    type=relation.type,
                    head_entity_id=new_head_id,
                    tail_entity_id=new_tail_id,
                    properties=relation.properties,
                    confidence=relation.confidence
                )
                updated_relations.append(updated_relation)
        
        # 融合关系
        relation_fusion_results = self.relation_fusion.batch_fuse_relations(updated_relations)
        
        # 清空当前关系
        self.relations.clear()
        self.relation_type_index.clear()
        self.graph.clear()
        
        # 重新添加实体到图中
        for entity in self.entities.values():
            self.graph.add_node(entity.id,
                               name=entity.name,
                               type=entity.type,
                               properties=entity.properties or {})
        
        # 添加融合后的关系
        for result in relation_fusion_results:
            self.add_relation(result.fused_relation)
    
    def detect_and_resolve_conflicts(self) -> List[Conflict]:
        """检测和解决冲突"""
        conflicts = []
        
        # 检测实体冲突
        entity_conflicts = self.conflict_resolver.detect_entity_conflicts(
            list(self.entities.values())
        )
        conflicts.extend(entity_conflicts)
        
        # 检测关系冲突
        relation_conflicts = self.conflict_resolver.detect_relation_conflicts(
            list(self.relations.values())
        )
        conflicts.extend(relation_conflicts)
        
        # 解决冲突
        resolved_conflicts = self.conflict_resolver.batch_resolve_conflicts(conflicts)
        
        return resolved_conflicts
    
    def validate_knowledge_graph(self) -> Dict[str, Any]:
        """验证知识图谱"""
        validation_results = {
            'valid': True,
            'issues': [],
            'statistics': {}
        }
        
        # 检查实体-关系一致性
        orphaned_relations = []
        for relation in self.relations.values():
            if (relation.head_entity_id not in self.entities or
                relation.tail_entity_id not in self.entities):
                orphaned_relations.append(relation.id)
        
        if orphaned_relations:
            validation_results['valid'] = False
            validation_results['issues'].append(
                f"发现 {len(orphaned_relations)} 个孤立关系"
            )
        
        # 检查本体一致性
        invalid_relations = []
        for relation in self.relations.values():
            head_entity = self.entities.get(relation.head_entity_id)
            tail_entity = self.entities.get(relation.tail_entity_id)
            
            if head_entity and tail_entity:
                if not self.ontology.validate_relation(relation.type,
                                                     head_entity.type,
                                                     tail_entity.type):
                    invalid_relations.append(relation.id)
        
        if invalid_relations:
            validation_results['valid'] = False
            validation_results['issues'].append(
                f"发现 {len(invalid_relations)} 个违反本体约束的关系"
            )
        
        # 统计信息
        validation_results['statistics'] = self.get_statistics()
        
        return validation_results
    
    def get_statistics(self) -> KnowledgeGraphStats:
        """获取知识图谱统计信息"""
        entity_types = defaultdict(int)
        for entity in self.entities.values():
            entity_types[entity.type] += 1
        
        relation_types = defaultdict(int)
        for relation in self.relations.values():
            relation_types[relation.type] += 1
        
        # 图统计
        node_count = self.graph.number_of_nodes()
        edge_count = self.graph.number_of_edges()
        
        avg_degree = (2 * edge_count / node_count) if node_count > 0 else 0
        connected_components = nx.number_weakly_connected_components(self.graph)
        density = nx.density(self.graph)
        
        return KnowledgeGraphStats(
            entity_count=len(self.entities),
            relation_count=len(self.relations),
            entity_types=dict(entity_types),
            relation_types=dict(relation_types),
            avg_degree=avg_degree,
            connected_components=connected_components,
            density=density
        )
    
    def export_to_json(self, filepath: str):
        """导出为JSON格式"""
        data = {
            'entities': [
                {
                    'id': entity.id,
                    'name': entity.name,
                    'type': entity.type,
                    'properties': entity.properties or {},
                    'aliases': entity.aliases or []
                }
                for entity in self.entities.values()
            ],
            'relations': [
                {
                    'id': relation.id,
                    'type': relation.type,
                    'head_entity_id': relation.head_entity_id,
                    'tail_entity_id': relation.tail_entity_id,
                    'properties': relation.properties or {},
                    'confidence': relation.confidence
                }
                for relation in self.relations.values()
            ],
            'statistics': self.get_statistics().__dict__
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def export_to_csv(self, entities_file: str, relations_file: str):
        """导出为CSV格式"""
        # 导出实体
        entity_data = []
        for entity in self.entities.values():
            entity_data.append({
                'id': entity.id,
                'name': entity.name,
                'type': entity.type,
                'aliases': ','.join(entity.aliases or []),
                'properties': json.dumps(entity.properties or {}, ensure_ascii=False)
            })
        
        entity_df = pd.DataFrame(entity_data)
        entity_df.to_csv(entities_file, index=False, encoding='utf-8')
        
        # 导出关系
        relation_data = []
        for relation in self.relations.values():
            relation_data.append({
                'id': relation.id,
                'type': relation.type,
                'head_entity_id': relation.head_entity_id,
                'tail_entity_id': relation.tail_entity_id,
                'confidence': relation.confidence,
                'properties': json.dumps(relation.properties or {}, ensure_ascii=False)
            })
        
        relation_df = pd.DataFrame(relation_data)
        relation_df.to_csv(relations_file, index=False, encoding='utf-8')
    
    def load_from_json(self, filepath: str):
        """从JSON文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 清空当前数据
        self.clear()
        
        # 加载实体
        for entity_data in data.get('entities', []):
            entity = Entity(
                id=entity_data['id'],
                name=entity_data['name'],
                type=entity_data['type'],
                properties=entity_data.get('properties', {}),
                aliases=entity_data.get('aliases', [])
            )
            self.add_entity(entity)
        
        # 加载关系
        for relation_data in data.get('relations', []):
            relation = Relation(
                id=relation_data['id'],
                type=relation_data['type'],
                head_entity_id=relation_data['head_entity_id'],
                tail_entity_id=relation_data['tail_entity_id'],
                properties=relation_data.get('properties', {}),
                confidence=relation_data.get('confidence', 1.0)
            )
            try:
                self.add_relation(relation)
            except ValueError:
                continue  # 跳过无效关系
    
    def visualize(self, output_file: str = None, layout: str = 'spring',
                  node_size_attr: str = None, edge_width_attr: str = None,
                  max_nodes: int = 50):
        """可视化知识图谱"""
        if len(self.entities) > max_nodes:
            print(f"实体数量 ({len(self.entities)}) 超过最大显示数量 ({max_nodes})")
            # 选择度数最高的节点
            degrees = dict(self.graph.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            subgraph_nodes = [node for node, _ in top_nodes]
            
            # 创建子图
            G = self.graph.subgraph(subgraph_nodes)
        else:
            G = self.graph
        
        plt.figure(figsize=(12, 8))
        
        # 选择布局
        if layout == 'spring':
            pos = nx.spring_layout(G, k=1, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(G)
        elif layout == 'random':
            pos = nx.random_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        # 节点大小
        if node_size_attr and node_size_attr in ['degree']:
            if node_size_attr == 'degree':
                node_sizes = [G.degree(node) * 100 + 300 for node in G.nodes()]
            else:
                node_sizes = 500
        else:
            node_sizes = 500
        
        # 绘制节点
        node_colors = []
        entity_types = set()
        for node in G.nodes():
            entity = self.entities.get(node)
            if entity:
                entity_types.add(entity.type)
        
        # 为不同实体类型分配颜色
        type_colors = plt.cm.Set3(range(len(entity_types)))
        type_color_map = {et: color for et, color in zip(entity_types, type_colors)}
        
        for node in G.nodes():
            entity = self.entities.get(node)
            if entity:
                node_colors.append(type_color_map.get(entity.type, 'lightblue'))
            else:
                node_colors.append('lightgray')
        
        # 绘制边
        edge_widths = []
        if edge_width_attr == 'confidence':
            for u, v, data in G.edges(data=True):
                confidence = data.get('confidence', 1.0)
                edge_widths.append(confidence * 3)
        else:
            edge_widths = 1
        
        # 绘制图
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.7)
        nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, 
                              edge_color='gray')
        
        # 添加标签
        labels = {}
        for node in G.nodes():
            entity = self.entities.get(node)
            if entity:
                # 限制标签长度
                label = entity.name[:10] + '...' if len(entity.name) > 10 else entity.name
                labels[node] = label
            else:
                labels[node] = node[:8]
        
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title(f"知识图谱可视化 ({len(G.nodes())} 实体, {len(G.edges())} 关系)")
        plt.axis('off')
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"图谱可视化已保存到: {output_file}")
        else:
            plt.show()
        
        plt.close()
    
    def clear(self):
        """清空知识图谱"""
        self.entities.clear()
        self.relations.clear()
        self.graph.clear()
        self.entity_type_index.clear()
        self.relation_type_index.clear()
        self.entity_name_index.clear()
    
    def print_summary(self):
        """打印知识图谱摘要"""
        stats = self.get_statistics()
        
        print("=" * 50)
        print("知识图谱摘要")
        print("=" * 50)
        print(f"实体数量: {stats.entity_count}")
        print(f"关系数量: {stats.relation_count}")
        print(f"平均度数: {stats.avg_degree:.2f}")
        print(f"连通分量: {stats.connected_components}")
        print(f"图密度: {stats.density:.4f}")
        
        print(f"\n实体类型分布:")
        for entity_type, count in sorted(stats.entity_types.items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"  {entity_type}: {count}")
        
        print(f"\n关系类型分布:")
        for relation_type, count in sorted(stats.relation_types.items(),
                                         key=lambda x: x[1], reverse=True):
            print(f"  {relation_type}: {count}")
        
        print("=" * 50)