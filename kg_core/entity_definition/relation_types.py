"""
关系类型管理模块
"""
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class Relation:
    """关系类"""
    id: str
    type: str
    head_entity_id: str
    tail_entity_id: str
    properties: Dict[str, Any]
    confidence: float = 1.0


class RelationTypes:
    """关系类型管理器"""
    
    def __init__(self):
        self.relations: Dict[str, Relation] = {}
        self.type_index: Dict[str, List[str]] = {}  # 按关系类型索引
        self.entity_index: Dict[str, List[str]] = {}  # 按实体索引关系
        self.head_tail_index: Dict[Tuple[str, str], List[str]] = {}  # 按头尾实体索引
    
    def add_relation(self, relation: Relation):
        """添加关系"""
        self.relations[relation.id] = relation
        
        # 更新类型索引
        if relation.type not in self.type_index:
            self.type_index[relation.type] = []
        self.type_index[relation.type].append(relation.id)
        
        # 更新实体索引
        for entity_id in [relation.head_entity_id, relation.tail_entity_id]:
            if entity_id not in self.entity_index:
                self.entity_index[entity_id] = []
            self.entity_index[entity_id].append(relation.id)
        
        # 更新头尾实体索引
        head_tail_key = (relation.head_entity_id, relation.tail_entity_id)
        if head_tail_key not in self.head_tail_index:
            self.head_tail_index[head_tail_key] = []
        self.head_tail_index[head_tail_key].append(relation.id)
    
    def get_relation(self, relation_id: str) -> Relation:
        """根据ID获取关系"""
        return self.relations.get(relation_id)
    
    def get_relations_by_type(self, relation_type: str) -> List[Relation]:
        """获取指定类型的所有关系"""
        relation_ids = self.type_index.get(relation_type, [])
        return [self.relations[rid] for rid in relation_ids]
    
    def get_relations_by_entity(self, entity_id: str) -> List[Relation]:
        """获取与指定实体相关的所有关系"""
        relation_ids = self.entity_index.get(entity_id, [])
        return [self.relations[rid] for rid in relation_ids]
    
    def get_relations_between_entities(self, head_entity_id: str, tail_entity_id: str) -> List[Relation]:
        """获取两个实体之间的所有关系"""
        relation_ids = self.head_tail_index.get((head_entity_id, tail_entity_id), [])
        return [self.relations[rid] for rid in relation_ids]
    
    def get_outgoing_relations(self, entity_id: str) -> List[Relation]:
        """获取实体的出边关系"""
        return [rel for rel in self.get_relations_by_entity(entity_id) 
                if rel.head_entity_id == entity_id]
    
    def get_incoming_relations(self, entity_id: str) -> List[Relation]:
        """获取实体的入边关系"""
        return [rel for rel in self.get_relations_by_entity(entity_id) 
                if rel.tail_entity_id == entity_id]
    
    def find_path(self, start_entity_id: str, end_entity_id: str, max_depth: int = 3) -> List[List[Relation]]:
        """找到两个实体之间的路径"""
        paths = []
        visited = set()
        current_path = []
        
        def dfs(current_entity_id: str, target_entity_id: str, depth: int):
            if depth > max_depth:
                return
            
            if current_entity_id == target_entity_id and len(current_path) > 0:
                paths.append(current_path.copy())
                return
            
            if current_entity_id in visited:
                return
            
            visited.add(current_entity_id)
            
            # 探索出边关系
            for relation in self.get_outgoing_relations(current_entity_id):
                current_path.append(relation)
                dfs(relation.tail_entity_id, target_entity_id, depth + 1)
                current_path.pop()
            
            visited.remove(current_entity_id)
        
        dfs(start_entity_id, end_entity_id, 0)
        return paths
    
    def update_relation_property(self, relation_id: str, property_name: str, value: Any):
        """更新关系属性"""
        if relation_id in self.relations:
            self.relations[relation_id].properties[property_name] = value
    
    def update_relation_confidence(self, relation_id: str, confidence: float):
        """更新关系置信度"""
        if relation_id in self.relations:
            self.relations[relation_id].confidence = confidence
    
    def delete_relation(self, relation_id: str):
        """删除关系"""
        if relation_id not in self.relations:
            return
        
        relation = self.relations[relation_id]
        
        # 从类型索引中移除
        if relation.type in self.type_index:
            self.type_index[relation.type].remove(relation_id)
        
        # 从实体索引中移除
        for entity_id in [relation.head_entity_id, relation.tail_entity_id]:
            if entity_id in self.entity_index:
                self.entity_index[entity_id].remove(relation_id)
        
        # 从头尾实体索引中移除
        head_tail_key = (relation.head_entity_id, relation.tail_entity_id)
        if head_tail_key in self.head_tail_index:
            self.head_tail_index[head_tail_key].remove(relation_id)
        
        # 删除关系
        del self.relations[relation_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "total_relations": len(self.relations),
            "by_type": {},
            "avg_confidence": 0.0
        }
        
        # 按类型统计
        for relation_type, relation_ids in self.type_index.items():
            stats["by_type"][relation_type] = len(relation_ids)
        
        # 平均置信度
        if self.relations:
            total_confidence = sum(rel.confidence for rel in self.relations.values())
            stats["avg_confidence"] = total_confidence / len(self.relations)
        
        return stats
    
    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()
        print(f"总关系数: {stats['total_relations']}")
        print(f"平均置信度: {stats['avg_confidence']:.2f}")
        print("按类型分布:")
        for relation_type, count in stats["by_type"].items():
            print(f"  {relation_type}: {count}")