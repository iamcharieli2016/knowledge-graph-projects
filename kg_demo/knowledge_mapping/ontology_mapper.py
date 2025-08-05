"""
本体映射模块 - 将抽取的知识映射到本体结构
"""
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import networkx as nx
from ..entity_definition.ontology import Ontology, EntityType, RelationType
from ..knowledge_extraction.entity_extractor import ExtractedEntity
from ..knowledge_extraction.relation_extractor import ExtractedRelation


@dataclass
class OntologyMapping:
    """本体映射结果"""
    source_type: str
    target_type: str
    mapping_confidence: float
    mapping_reason: str


class OntologyMapper:
    """本体映射器"""
    
    def __init__(self, source_ontology: Ontology, target_ontology: Ontology = None):
        self.source_ontology = source_ontology
        self.target_ontology = target_ontology or source_ontology
        self.entity_type_mappings: Dict[str, str] = {}
        self.relation_type_mappings: Dict[str, str] = {}
        self.concept_hierarchy = self._build_concept_hierarchy()
    
    def _build_concept_hierarchy(self) -> nx.DiGraph:
        """构建概念层次结构图"""
        graph = nx.DiGraph()
        
        # 添加实体类型节点
        for entity_type_name, entity_type in self.source_ontology.entity_types.items():
            graph.add_node(entity_type_name, type='entity', data=entity_type)
            
            # 添加父子关系
            if entity_type.parent_type:
                graph.add_edge(entity_type.parent_type, entity_type_name, relation='subclass_of')
        
        # 添加关系类型节点
        for relation_type_name, relation_type in self.source_ontology.relation_types.items():
            graph.add_node(relation_type_name, type='relation', data=relation_type)
            
            # 添加定义域和值域的连接
            if relation_type.domain in graph.nodes:
                graph.add_edge(relation_type_name, relation_type.domain, relation='has_domain')
            if relation_type.range in graph.nodes:
                graph.add_edge(relation_type_name, relation_type.range, relation='has_range')
        
        return graph
    
    def find_similar_entity_types(self, entity_type_name: str, 
                                 target_ontology: Ontology = None) -> List[Tuple[str, float]]:
        """查找相似的实体类型"""
        if not target_ontology:
            target_ontology = self.target_ontology
        
        source_type = self.source_ontology.get_entity_type(entity_type_name)
        if not source_type:
            return []
        
        candidates = []
        
        for target_type_name, target_type in target_ontology.entity_types.items():
            similarity = self._calculate_entity_type_similarity(source_type, target_type)
            if similarity > 0.3:  # 阈值
                candidates.append((target_type_name, similarity))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def find_similar_relation_types(self, relation_type_name: str,
                                   target_ontology: Ontology = None) -> List[Tuple[str, float]]:
        """查找相似的关系类型"""
        if not target_ontology:
            target_ontology = self.target_ontology
        
        source_type = self.source_ontology.get_relation_type(relation_type_name)
        if not source_type:
            return []
        
        candidates = []
        
        for target_type_name, target_type in target_ontology.relation_types.items():
            similarity = self._calculate_relation_type_similarity(source_type, target_type)
            if similarity > 0.3:
                candidates.append((target_type_name, similarity))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def _calculate_entity_type_similarity(self, source_type: EntityType, 
                                        target_type: EntityType) -> float:
        """计算实体类型相似度"""
        similarity = 0.0
        
        # 名称相似度
        name_similarity = self._calculate_string_similarity(source_type.name, target_type.name)
        similarity += name_similarity * 0.4
        
        # 描述相似度
        desc_similarity = self._calculate_string_similarity(
            source_type.description, target_type.description
        )
        similarity += desc_similarity * 0.3
        
        # 属性相似度
        prop_similarity = self._calculate_property_similarity(
            source_type.properties, target_type.properties
        )
        similarity += prop_similarity * 0.3
        
        return min(similarity, 1.0)
    
    def _calculate_relation_type_similarity(self, source_type: RelationType,
                                          target_type: RelationType) -> float:
        """计算关系类型相似度"""
        similarity = 0.0
        
        # 名称相似度
        name_similarity = self._calculate_string_similarity(source_type.name, target_type.name)
        similarity += name_similarity * 0.4
        
        # 描述相似度
        desc_similarity = self._calculate_string_similarity(
            source_type.description, target_type.description
        )
        similarity += desc_similarity * 0.3
        
        # 定义域和值域相似度
        domain_similarity = 1.0 if source_type.domain == target_type.domain else 0.0
        range_similarity = 1.0 if source_type.range == target_type.range else 0.0
        similarity += (domain_similarity + range_similarity) * 0.15
        
        return min(similarity, 1.0)
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        if not str1 or not str2:
            return 0.0
        
        # 简单的字符级Jaccard相似度
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_property_similarity(self, props1: List[str], props2: List[str]) -> float:
        """计算属性列表相似度"""
        if not props1 and not props2:
            return 1.0
        if not props1 or not props2:
            return 0.0
        
        set1 = set(props1)
        set2 = set(props2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def map_entity_type(self, entity_type_name: str) -> OntologyMapping:
        """映射实体类型"""
        # 检查是否已有映射
        if entity_type_name in self.entity_type_mappings:
            target_type = self.entity_type_mappings[entity_type_name]
            return OntologyMapping(
                source_type=entity_type_name,
                target_type=target_type,
                mapping_confidence=1.0,
                mapping_reason="预定义映射"
            )
        
        # 查找相似类型
        similar_types = self.find_similar_entity_types(entity_type_name)
        
        if similar_types:
            best_match, confidence = similar_types[0]
            return OntologyMapping(
                source_type=entity_type_name,
                target_type=best_match,
                mapping_confidence=confidence,
                mapping_reason="相似度匹配"
            )
        else:
            return OntologyMapping(
                source_type=entity_type_name,
                target_type=entity_type_name,  # 保持原类型
                mapping_confidence=0.5,
                mapping_reason="无匹配，保持原类型"
            )
    
    def map_relation_type(self, relation_type_name: str) -> OntologyMapping:
        """映射关系类型"""
        # 检查是否已有映射
        if relation_type_name in self.relation_type_mappings:
            target_type = self.relation_type_mappings[relation_type_name]
            return OntologyMapping(
                source_type=relation_type_name,
                target_type=target_type,
                mapping_confidence=1.0,
                mapping_reason="预定义映射"
            )
        
        # 查找相似类型
        similar_types = self.find_similar_relation_types(relation_type_name)
        
        if similar_types:
            best_match, confidence = similar_types[0]
            return OntologyMapping(
                source_type=relation_type_name,
                target_type=best_match,
                mapping_confidence=confidence,
                mapping_reason="相似度匹配"
            )
        else:
            return OntologyMapping(
                source_type=relation_type_name,
                target_type=relation_type_name,
                mapping_confidence=0.5,
                mapping_reason="无匹配，保持原类型"
            )
    
    def infer_entity_type_from_context(self, extracted_entity: ExtractedEntity,
                                      context_relations: List[ExtractedRelation]) -> List[Tuple[str, float]]:
        """基于上下文推断实体类型"""
        type_candidates = {}
        
        # 分析与该实体相关的关系
        for relation in context_relations:
            if relation.head_entity == extracted_entity.text:
                # 该实体作为头实体
                relation_type = self.source_ontology.get_relation_type(relation.relation_type)
                if relation_type and relation_type.domain:
                    type_candidates[relation_type.domain] = \
                        type_candidates.get(relation_type.domain, 0) + 0.5
            
            elif relation.tail_entity == extracted_entity.text:
                # 该实体作为尾实体
                relation_type = self.source_ontology.get_relation_type(relation.relation_type)
                if relation_type and relation_type.range:
                    type_candidates[relation_type.range] = \
                        type_candidates.get(relation_type.range, 0) + 0.5
        
        # 按置信度排序
        candidates = [(entity_type, confidence) for entity_type, confidence in type_candidates.items()]
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates
    
    def validate_mapping_consistency(self, mappings: List[OntologyMapping]) -> Dict[str, List[str]]:
        """验证映射一致性"""
        issues = {
            'conflicts': [],
            'missing_mappings': [],
            'circular_dependencies': []
        }
        
        # 检查映射冲突
        target_types = {}
        for mapping in mappings:
            if mapping.target_type in target_types:
                issues['conflicts'].append(
                    f"类型 {mapping.target_type} 被多个源类型映射: "
                    f"{target_types[mapping.target_type]} 和 {mapping.source_type}"
                )
            else:
                target_types[mapping.target_type] = mapping.source_type
        
        # 检查缺失的映射
        all_source_types = set(self.source_ontology.entity_types.keys()) | \
                          set(self.source_ontology.relation_types.keys())
        mapped_types = {mapping.source_type for mapping in mappings}
        
        missing_types = all_source_types - mapped_types
        if missing_types:
            issues['missing_mappings'].extend(list(missing_types))
        
        return issues
    
    def suggest_ontology_extensions(self, extracted_entities: List[ExtractedEntity],
                                  extracted_relations: List[ExtractedRelation]) -> Dict[str, List[str]]:
        """建议本体扩展"""
        suggestions = {
            'new_entity_types': [],
            'new_relation_types': [],
            'new_properties': []
        }
        
        # 分析未映射的实体类型
        entity_types_in_use = {entity.type for entity in extracted_entities}
        existing_entity_types = set(self.source_ontology.entity_types.keys())
        
        new_entity_types = entity_types_in_use - existing_entity_types
        suggestions['new_entity_types'].extend(list(new_entity_types))
        
        # 分析未映射的关系类型
        relation_types_in_use = {relation.relation_type for relation in extracted_relations}
        existing_relation_types = set(self.source_ontology.relation_types.keys())
        
        new_relation_types = relation_types_in_use - existing_relation_types
        suggestions['new_relation_types'].extend(list(new_relation_types))
        
        # 分析新属性
        all_properties = set()
        for entity in extracted_entities:
            if hasattr(entity, 'properties') and entity.properties:
                all_properties.update(entity.properties.keys())
        
        existing_properties = set()
        for entity_type in self.source_ontology.entity_types.values():
            existing_properties.update(entity_type.properties)
        
        new_properties = all_properties - existing_properties
        suggestions['new_properties'].extend(list(new_properties))
        
        return suggestions
    
    def apply_mappings(self, mappings: List[OntologyMapping]):
        """应用映射结果"""
        for mapping in mappings:
            if mapping.mapping_confidence > 0.7:  # 只应用高置信度的映射
                if mapping.source_type in self.source_ontology.entity_types:
                    self.entity_type_mappings[mapping.source_type] = mapping.target_type
                elif mapping.source_type in self.source_ontology.relation_types:
                    self.relation_type_mappings[mapping.source_type] = mapping.target_type
    
    def get_concept_path(self, concept1: str, concept2: str) -> Optional[List[str]]:
        """获取两个概念之间的路径"""
        try:
            path = nx.shortest_path(self.concept_hierarchy, concept1, concept2)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_concept_similarity_by_path(self, concept1: str, concept2: str) -> float:
        """基于路径的概念相似度"""
        if concept1 == concept2:
            return 1.0
        
        path = self.get_concept_path(concept1, concept2)
        if path is None:
            return 0.0
        
        # 路径越短，相似度越高
        path_length = len(path) - 1
        max_possible_length = 10  # 假设的最大路径长度
        
        similarity = max(0.0, 1.0 - (path_length / max_possible_length))
        return similarity
    
    def print_mapping_results(self, mappings: List[OntologyMapping]):
        """打印映射结果"""
        print(f"本体映射结果 ({len(mappings)} 个映射):")
        
        entity_mappings = [m for m in mappings if m.source_type in self.source_ontology.entity_types]
        relation_mappings = [m for m in mappings if m.source_type in self.source_ontology.relation_types]
        
        print(f"\n实体类型映射 ({len(entity_mappings)}):")
        for mapping in entity_mappings:
            print(f"  {mapping.source_type} -> {mapping.target_type} "
                  f"(置信度: {mapping.mapping_confidence:.2f}, 原因: {mapping.mapping_reason})")
        
        print(f"\n关系类型映射 ({len(relation_mappings)}):")
        for mapping in relation_mappings:
            print(f"  {mapping.source_type} -> {mapping.target_type} "
                  f"(置信度: {mapping.mapping_confidence:.2f}, 原因: {mapping.mapping_reason})")