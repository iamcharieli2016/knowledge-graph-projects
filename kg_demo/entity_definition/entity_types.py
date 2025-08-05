"""
实体类型管理模块
"""
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class Entity:
    """实体类"""
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    aliases: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class EntityTypes:
    """实体类型管理器"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.type_index: Dict[str, List[str]] = {}  # 按类型索引实体
        self.name_index: Dict[str, str] = {}  # 按名称索引实体ID
    
    def add_entity(self, entity: Entity):
        """添加实体"""
        self.entities[entity.id] = entity
        
        # 更新类型索引
        if entity.type not in self.type_index:
            self.type_index[entity.type] = []
        self.type_index[entity.type].append(entity.id)
        
        # 更新名称索引
        self.name_index[entity.name] = entity.id
        for alias in entity.aliases:
            self.name_index[alias] = entity.id
    
    def get_entity(self, entity_id: str) -> Entity:
        """根据ID获取实体"""
        return self.entities.get(entity_id)
    
    def get_entity_by_name(self, name: str) -> Entity:
        """根据名称获取实体"""
        entity_id = self.name_index.get(name)
        if entity_id:
            return self.entities.get(entity_id)
        return None
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """获取指定类型的所有实体"""
        entity_ids = self.type_index.get(entity_type, [])
        return [self.entities[eid] for eid in entity_ids]
    
    def search_entities(self, query: str, entity_type: str = None) -> List[Entity]:
        """搜索实体"""
        results = []
        for entity in self.entities.values():
            if entity_type and entity.type != entity_type:
                continue
            
            # 检查名称匹配
            if query.lower() in entity.name.lower():
                results.append(entity)
                continue
            
            # 检查别名匹配
            for alias in entity.aliases:
                if query.lower() in alias.lower():
                    results.append(entity)
                    break
        
        return results
    
    def update_entity_property(self, entity_id: str, property_name: str, value: Any):
        """更新实体属性"""
        if entity_id in self.entities:
            self.entities[entity_id].properties[property_name] = value
    
    def delete_entity(self, entity_id: str):
        """删除实体"""
        if entity_id not in self.entities:
            return
        
        entity = self.entities[entity_id]
        
        # 从类型索引中移除
        if entity.type in self.type_index:
            self.type_index[entity.type].remove(entity_id)
        
        # 从名称索引中移除
        del self.name_index[entity.name]
        for alias in entity.aliases:
            if alias in self.name_index:
                del self.name_index[alias]
        
        # 删除实体
        del self.entities[entity_id]
    
    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        stats = {
            "total_entities": len(self.entities),
            "by_type": {}
        }
        
        for entity_type, entity_ids in self.type_index.items():
            stats["by_type"][entity_type] = len(entity_ids)
        
        return stats
    
    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()
        print(f"总实体数: {stats['total_entities']}")
        print("按类型分布:")
        for entity_type, count in stats["by_type"].items():
            print(f"  {entity_type}: {count}")