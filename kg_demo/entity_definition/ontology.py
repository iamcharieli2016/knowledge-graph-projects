"""
本体定义模块 - 定义知识图谱的本体结构
"""
from typing import Dict, List, Set
from dataclasses import dataclass
import json


@dataclass
class EntityType:
    """实体类型定义"""
    name: str
    description: str
    properties: List[str]
    parent_type: str = None


@dataclass
class RelationType:
    """关系类型定义"""
    name: str
    description: str
    domain: str  # 头实体类型
    range: str   # 尾实体类型
    properties: List[str] = None


class Ontology:
    """本体管理类"""
    
    def __init__(self):
        self.entity_types: Dict[str, EntityType] = {}
        self.relation_types: Dict[str, RelationType] = {}
        self.initialize_default_ontology()
    
    def initialize_default_ontology(self):
        """初始化默认本体"""
        # 定义实体类型
        entity_types = [
            EntityType("Person", "人物实体", ["name", "age", "occupation", "nationality"]),
            EntityType("Organization", "组织机构", ["name", "type", "founded_year", "location"]),
            EntityType("Location", "地理位置", ["name", "type", "coordinates", "population"]),
            EntityType("Event", "事件", ["name", "date", "location", "participants"]),
            EntityType("Product", "产品", ["name", "category", "price", "manufacturer"]),
            EntityType("Concept", "概念", ["name", "definition", "category"])
        ]
        
        for entity_type in entity_types:
            self.add_entity_type(entity_type)
        
        # 定义关系类型
        relation_types = [
            RelationType("works_for", "工作于", "Person", "Organization"),
            RelationType("located_in", "位于", "Organization", "Location"),
            RelationType("born_in", "出生于", "Person", "Location"),
            RelationType("participated_in", "参与", "Person", "Event"),
            RelationType("occurred_at", "发生于", "Event", "Location"),
            RelationType("produces", "生产", "Organization", "Product"),
            RelationType("founder_of", "创始人", "Person", "Organization"),
            RelationType("parent_of", "父母", "Person", "Person"),
            RelationType("spouse_of", "配偶", "Person", "Person"),
            RelationType("friend_of", "朋友", "Person", "Person")
        ]
        
        for relation_type in relation_types:
            self.add_relation_type(relation_type)
    
    def add_entity_type(self, entity_type: EntityType):
        """添加实体类型"""
        self.entity_types[entity_type.name] = entity_type
    
    def add_relation_type(self, relation_type: RelationType):
        """添加关系类型"""
        self.relation_types[relation_type.name] = relation_type
    
    def get_entity_type(self, name: str) -> EntityType:
        """获取实体类型"""
        return self.entity_types.get(name)
    
    def get_relation_type(self, name: str) -> RelationType:
        """获取关系类型"""
        return self.relation_types.get(name)
    
    def validate_relation(self, relation_name: str, head_entity_type: str, tail_entity_type: str) -> bool:
        """验证关系是否符合本体定义"""
        relation_type = self.get_relation_type(relation_name)
        if not relation_type:
            return False
        
        return (relation_type.domain == head_entity_type and 
                relation_type.range == tail_entity_type)
    
    def get_possible_relations(self, head_type: str, tail_type: str) -> List[str]:
        """获取两个实体类型之间可能的关系"""
        possible_relations = []
        for rel_name, rel_type in self.relation_types.items():
            if rel_type.domain == head_type and rel_type.range == tail_type:
                possible_relations.append(rel_name)
        return possible_relations
    
    def export_ontology(self, filepath: str):
        """导出本体到JSON文件"""
        ontology_data = {
            "entity_types": {
                name: {
                    "description": et.description,
                    "properties": et.properties,
                    "parent_type": et.parent_type
                }
                for name, et in self.entity_types.items()
            },
            "relation_types": {
                name: {
                    "description": rt.description,
                    "domain": rt.domain,
                    "range": rt.range,
                    "properties": rt.properties
                }
                for name, rt in self.relation_types.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(ontology_data, f, ensure_ascii=False, indent=2)
    
    def load_ontology(self, filepath: str):
        """从JSON文件加载本体"""
        with open(filepath, 'r', encoding='utf-8') as f:
            ontology_data = json.load(f)
        
        # 加载实体类型
        for name, data in ontology_data.get("entity_types", {}).items():
            entity_type = EntityType(
                name=name,
                description=data["description"],
                properties=data["properties"],
                parent_type=data.get("parent_type")
            )
            self.add_entity_type(entity_type)
        
        # 加载关系类型
        for name, data in ontology_data.get("relation_types", {}).items():
            relation_type = RelationType(
                name=name,
                description=data["description"],
                domain=data["domain"],
                range=data["range"],
                properties=data.get("properties", [])
            )
            self.add_relation_type(relation_type)
    
    def print_ontology_summary(self):
        """打印本体摘要"""
        print("=== 知识图谱本体摘要 ===")
        print(f"\n实体类型 ({len(self.entity_types)}):")
        for name, entity_type in self.entity_types.items():
            print(f"  - {name}: {entity_type.description}")
        
        print(f"\n关系类型 ({len(self.relation_types)}):")
        for name, relation_type in self.relation_types.items():
            print(f"  - {name}: {relation_type.domain} -> {relation_type.range}")