"""
关系映射模块 - 将抽取的关系映射到本体中的标准关系
"""
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from ..knowledge_extraction.relation_extractor import ExtractedRelation
from ..entity_definition.relation_types import Relation
from ..entity_definition.ontology import Ontology


@dataclass
class RelationMapping:
    """关系映射结果"""
    extracted_relation: ExtractedRelation
    mapped_relation_type: Optional[str]
    confidence: float
    mapping_type: str  # 'direct', 'inferred', 'new'
    validation_result: bool = True


class RelationMapper:
    """关系映射器"""
    
    def __init__(self, ontology: Ontology):
        self.ontology = ontology
        self.relation_synonyms = self._build_relation_synonyms()
        self.relation_patterns = self._build_relation_patterns()
        self.confidence_threshold = 0.6
    
    def _build_relation_synonyms(self) -> Dict[str, List[str]]:
        """构建关系同义词映射"""
        synonyms = {
            'works_for': ['工作于', '就职于', '任职于', '在', '供职于', '服务于'],
            'located_in': ['位于', '在', '坐落于', '设在', '建在', '处于'],
            'born_in': ['出生于', '生于', '出生在', '来自'],
            'founder_of': ['创建', '创立', '创办', '成立', '建立', '开创'],
            'participated_in': ['参加', '参与', '出席', '加入', '参会'],
            'produces': ['生产', '制造', '开发', '研发', '推出', '发布'],
            'occurred_at': ['发生在', '举行于', '进行于', '在...举行'],
            'parent_of': ['父亲', '母亲', '父母', '爸爸', '妈妈'],
            'spouse_of': ['丈夫', '妻子', '配偶', '夫妻', '老公', '老婆'],
            'friend_of': ['朋友', '好友', '友人', '伙伴']
        }
        
        # 反向映射
        reverse_map = {}
        for relation_type, synonym_list in synonyms.items():
            for synonym in synonym_list:
                reverse_map[synonym] = relation_type
        
        return reverse_map
    
    def _build_relation_patterns(self) -> Dict[str, List[str]]:
        """构建关系模式映射"""
        patterns = {
            'works_for': [
                r'.*(?:在|就职于|工作于).*',
                r'.*(?:是|担任).*(?:员工|职员|经理|总监).*'
            ],
            'located_in': [
                r'.*(?:位于|坐落于|设在).*',
                r'.*总部.*(?:在|位于).*'
            ],
            'founder_of': [
                r'.*(?:创建|创立|创办).*',
                r'.*(?:创始人|创办者).*'
            ]
        }
        return patterns
    
    def direct_mapping(self, extracted_relation: ExtractedRelation) -> Optional[str]:
        """直接映射 - 基于关系类型名称"""
        # 检查是否为已知的关系类型
        if self.ontology.get_relation_type(extracted_relation.relation_type):
            return extracted_relation.relation_type
        
        # 检查同义词映射
        if extracted_relation.relation_type in self.relation_synonyms:
            return self.relation_synonyms[extracted_relation.relation_type]
        
        return None
    
    def context_based_mapping(self, extracted_relation: ExtractedRelation) -> List[Tuple[str, float]]:
        """基于上下文的关系映射"""
        candidates = []
        context = extracted_relation.context.lower()
        
        for relation_type, synonyms in self.relation_synonyms.items():
            confidence = 0.0
            
            # 检查同义词在上下文中出现
            for synonym in synonyms:
                if synonym in context:
                    confidence += 0.2
            
            # 检查模式匹配
            if relation_type in self.relation_patterns:
                for pattern in self.relation_patterns[relation_type]:
                    import re
                    if re.search(pattern, context):
                        confidence += 0.3
            
            if confidence > 0:
                candidates.append((relation_type, min(confidence, 1.0)))
        
        # 按置信度排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def entity_type_based_mapping(self, extracted_relation: ExtractedRelation, 
                                 head_entity_type: str, tail_entity_type: str) -> List[Tuple[str, float]]:
        """基于实体类型的关系推断"""
        candidates = []
        
        # 获取两个实体类型之间可能的关系
        possible_relations = self.ontology.get_possible_relations(head_entity_type, tail_entity_type)
        
        for relation_type in possible_relations:
            # 基础置信度
            confidence = 0.5
            
            # 如果上下文中包含相关词汇，提高置信度
            context = extracted_relation.context.lower()
            relation_synonyms = [k for k, v in self.relation_synonyms.items() if v == relation_type]
            
            for synonym in relation_synonyms:
                if synonym in context:
                    confidence += 0.2
            
            candidates.append((relation_type, min(confidence, 1.0)))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def semantic_similarity_mapping(self, extracted_relation: ExtractedRelation) -> List[Tuple[str, float]]:
        """语义相似度映射（简化版）"""
        candidates = []
        
        # 基于词汇重叠的简单语义相似度
        relation_words = extracted_relation.relation_type.lower().split()
        
        for relation_type in self.ontology.relation_types.keys():
            # 计算词汇相似度
            target_words = relation_type.lower().split('_')
            
            overlap = set(relation_words) & set(target_words)
            if overlap:
                similarity = len(overlap) / max(len(relation_words), len(target_words))
                candidates.append((relation_type, similarity))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def validate_relation_mapping(self, relation_type: str, head_entity_type: str, 
                                tail_entity_type: str) -> bool:
        """验证关系映射是否符合本体约束"""
        return self.ontology.validate_relation(relation_type, head_entity_type, tail_entity_type)
    
    def map_relation(self, extracted_relation: ExtractedRelation, 
                    head_entity_type: str = None, tail_entity_type: str = None) -> RelationMapping:
        """映射关系"""
        
        # 1. 尝试直接映射
        direct_result = self.direct_mapping(extracted_relation)
        if direct_result:
            # 验证映射结果
            validation_result = True
            if head_entity_type and tail_entity_type:
                validation_result = self.validate_relation_mapping(
                    direct_result, head_entity_type, tail_entity_type
                )
            
            return RelationMapping(
                extracted_relation=extracted_relation,
                mapped_relation_type=direct_result,
                confidence=0.9,
                mapping_type='direct',
                validation_result=validation_result
            )
        
        # 2. 基于上下文的映射
        context_candidates = self.context_based_mapping(extracted_relation)
        
        # 3. 基于实体类型的映射
        entity_type_candidates = []
        if head_entity_type and tail_entity_type:
            entity_type_candidates = self.entity_type_based_mapping(
                extracted_relation, head_entity_type, tail_entity_type
            )
        
        # 4. 语义相似度映射
        semantic_candidates = self.semantic_similarity_mapping(extracted_relation)
        
        # 综合所有候选结果
        all_candidates = {}
        
        # 合并候选结果，累加置信度
        for relation_type, confidence in context_candidates:
            all_candidates[relation_type] = all_candidates.get(relation_type, 0) + confidence * 0.4
        
        for relation_type, confidence in entity_type_candidates:
            all_candidates[relation_type] = all_candidates.get(relation_type, 0) + confidence * 0.4
        
        for relation_type, confidence in semantic_candidates:
            all_candidates[relation_type] = all_candidates.get(relation_type, 0) + confidence * 0.2
        
        if all_candidates:
            # 选择最佳候选
            best_relation_type = max(all_candidates.items(), key=lambda x: x[1])
            relation_type, confidence = best_relation_type
            
            # 验证映射结果
            validation_result = True
            if head_entity_type and tail_entity_type:
                validation_result = self.validate_relation_mapping(
                    relation_type, head_entity_type, tail_entity_type
                )
            
            mapping_type = 'inferred' if confidence > self.confidence_threshold else 'new'
            
            return RelationMapping(
                extracted_relation=extracted_relation,
                mapped_relation_type=relation_type if validation_result else None,
                confidence=confidence,
                mapping_type=mapping_type,
                validation_result=validation_result
            )
        
        # 5. 创建新关系类型
        return RelationMapping(
            extracted_relation=extracted_relation,
            mapped_relation_type=None,
            confidence=0.0,
            mapping_type='new',
            validation_result=False
        )
    
    def batch_map_relations(self, extracted_relations: List[ExtractedRelation],
                          entity_type_mapping: Dict[str, str] = None) -> List[RelationMapping]:
        """批量映射关系"""
        mappings = []
        
        for extracted_relation in extracted_relations:
            # 获取实体类型信息
            head_entity_type = None
            tail_entity_type = None
            
            if entity_type_mapping:
                head_entity_type = entity_type_mapping.get(extracted_relation.head_entity)
                tail_entity_type = entity_type_mapping.get(extracted_relation.tail_entity)
            
            mapping = self.map_relation(extracted_relation, head_entity_type, tail_entity_type)
            mappings.append(mapping)
        
        return mappings
    
    def resolve_relation_conflicts(self, mappings: List[RelationMapping]) -> List[RelationMapping]:
        """解决关系映射冲突"""
        resolved_mappings = []
        
        # 按(头实体, 尾实体)分组
        relation_groups = {}
        for mapping in mappings:
            key = (mapping.extracted_relation.head_entity, mapping.extracted_relation.tail_entity)
            if key not in relation_groups:
                relation_groups[key] = []
            relation_groups[key].append(mapping)
        
        # 解决每组内的冲突
        for group in relation_groups.values():
            if len(group) == 1:
                resolved_mappings.extend(group)
            else:
                # 选择置信度最高的映射
                best_mapping = max(group, key=lambda x: x.confidence)
                resolved_mappings.append(best_mapping)
        
        return resolved_mappings
    
    def suggest_new_relation_type(self, extracted_relation: ExtractedRelation,
                                head_entity_type: str, tail_entity_type: str) -> Dict[str, str]:
        """为新关系建议关系类型定义"""
        # 基于实体类型和上下文生成关系类型名称
        relation_name = f"{head_entity_type.lower()}_{tail_entity_type.lower()}_relation"
        
        # 基于上下文生成描述
        context_words = extracted_relation.context.split()
        key_words = [word for word in context_words if len(word) > 2][:3]
        description = f"关系类型基于上下文: {' '.join(key_words)}"
        
        return {
            'name': relation_name,
            'description': description,
            'domain': head_entity_type,
            'range': tail_entity_type,
            'examples': [f"{extracted_relation.head_entity} -> {extracted_relation.tail_entity}"]
        }
    
    def get_mapping_statistics(self, mappings: List[RelationMapping]) -> Dict[str, int]:
        """获取关系映射统计信息"""
        stats = {
            'total': len(mappings),
            'direct': 0,
            'inferred': 0,
            'new': 0,
            'valid': 0,
            'invalid': 0,
            'high_confidence': 0,  # > 0.8
            'medium_confidence': 0,  # 0.5 - 0.8
            'low_confidence': 0  # < 0.5
        }
        
        for mapping in mappings:
            stats[mapping.mapping_type] += 1
            
            if mapping.validation_result:
                stats['valid'] += 1
            else:
                stats['invalid'] += 1
            
            if mapping.confidence > 0.8:
                stats['high_confidence'] += 1
            elif mapping.confidence > 0.5:
                stats['medium_confidence'] += 1
            else:
                stats['low_confidence'] += 1
        
        return stats
    
    def print_mapping_results(self, mappings: List[RelationMapping]):
        """打印关系映射结果"""
        stats = self.get_mapping_statistics(mappings)
        
        print(f"关系映射结果 ({stats['total']} 个关系):")
        print(f"  直接映射: {stats['direct']}")
        print(f"  推断映射: {stats['inferred']}")
        print(f"  新关系: {stats['new']}")
        
        print(f"\n验证结果:")
        print(f"  有效: {stats['valid']}")
        print(f"  无效: {stats['invalid']}")
        
        print(f"\n置信度分布:")
        print(f"  高置信度 (>0.8): {stats['high_confidence']}")
        print(f"  中等置信度 (0.5-0.8): {stats['medium_confidence']}")
        print(f"  低置信度 (<0.5): {stats['low_confidence']}")
        
        # 显示一些具体的映射示例
        print(f"\n映射示例:")
        for i, mapping in enumerate(mappings[:5]):
            relation_type = mapping.mapped_relation_type or "新关系类型"
            validation = "✓" if mapping.validation_result else "✗"
            print(f"  {mapping.extracted_relation.head_entity} -[{relation_type}]-> "
                  f"{mapping.extracted_relation.tail_entity} "
                  f"({mapping.mapping_type}, {validation}, 置信度: {mapping.confidence:.2f})")