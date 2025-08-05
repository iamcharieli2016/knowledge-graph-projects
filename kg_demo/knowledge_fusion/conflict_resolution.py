"""
冲突解决模块 - 处理知识融合过程中的冲突
"""
from typing import List, Dict, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter
import logging
from ..entity_definition.entity_types import Entity
from ..entity_definition.relation_types import Relation


class ConflictType(Enum):
    """冲突类型"""
    ENTITY_NAME_CONFLICT = "entity_name_conflict"
    ENTITY_TYPE_CONFLICT = "entity_type_conflict" 
    PROPERTY_VALUE_CONFLICT = "property_value_conflict"
    RELATION_TYPE_CONFLICT = "relation_type_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"
    CONTRADICTORY_RELATIONS = "contradictory_relations"


@dataclass
class Conflict:
    """冲突"""
    conflict_id: str
    conflict_type: ConflictType
    description: str
    conflicting_items: List[Any]
    confidence_scores: List[float]
    resolution_strategy: Optional[str] = None
    resolved_value: Optional[Any] = None
    resolution_confidence: float = 0.0


class ConflictResolver:
    """冲突解决器"""
    
    def __init__(self):
        self.resolution_strategies = self._build_resolution_strategies()
        self.conflict_history = []
        self.logger = logging.getLogger(__name__)
    
    def _build_resolution_strategies(self) -> Dict[ConflictType, List[str]]:
        """构建冲突解决策略"""
        strategies = {
            ConflictType.ENTITY_NAME_CONFLICT: [
                'highest_confidence',
                'most_frequent',
                'longest_name',
                'manual_review'
            ],
            ConflictType.ENTITY_TYPE_CONFLICT: [
                'most_specific_type',
                'highest_confidence',
                'vote',
                'hierarchy_based'
            ],
            ConflictType.PROPERTY_VALUE_CONFLICT: [
                'highest_confidence',
                'most_recent',
                'vote',
                'average_numeric',
                'union_lists'
            ],
            ConflictType.RELATION_TYPE_CONFLICT: [
                'highest_confidence',
                'most_frequent',
                'semantic_similarity',
                'manual_review'
            ],
            ConflictType.TEMPORAL_CONFLICT: [
                'most_recent',
                'longest_duration',
                'highest_confidence'
            ],
            ConflictType.CONTRADICTORY_RELATIONS: [
                'highest_confidence',
                'source_authority',
                'temporal_precedence',
                'manual_review'
            ]
        }
        return strategies
    
    def detect_entity_conflicts(self, entities: List[Entity]) -> List[Conflict]:
        """检测实体冲突"""
        conflicts = []
        
        # 按ID分组实体
        entity_groups = defaultdict(list)
        for entity in entities:
            entity_groups[entity.id].append(entity)
        
        # 检查每组内的冲突
        for entity_id, group in entity_groups.items():
            if len(group) <= 1:
                continue
            
            # 检测名称冲突
            names = [entity.name for entity in group]
            if len(set(names)) > 1:
                conflict = Conflict(
                    conflict_id=f"name_conflict_{entity_id}",
                    conflict_type=ConflictType.ENTITY_NAME_CONFLICT,
                    description=f"实体 {entity_id} 有多个不同的名称",
                    conflicting_items=names,
                    confidence_scores=[1.0] * len(names)  # 简化处理
                )
                conflicts.append(conflict)
            
            # 检测类型冲突
            types = [entity.type for entity in group]
            if len(set(types)) > 1:
                conflict = Conflict(
                    conflict_id=f"type_conflict_{entity_id}",
                    conflict_type=ConflictType.ENTITY_TYPE_CONFLICT,
                    description=f"实体 {entity_id} 有多个不同的类型",
                    conflicting_items=types,
                    confidence_scores=[1.0] * len(types)
                )
                conflicts.append(conflict)
            
            # 检测属性值冲突
            property_conflicts = self._detect_property_conflicts(group, entity_id)
            conflicts.extend(property_conflicts)
        
        return conflicts
    
    def _detect_property_conflicts(self, entities: List[Entity], entity_id: str) -> List[Conflict]:
        """检测属性值冲突"""
        conflicts = []
        
        # 收集所有属性键
        all_properties = defaultdict(list)
        for entity in entities:
            if entity.properties:
                for key, value in entity.properties.items():
                    all_properties[key].append(value)
        
        # 检查每个属性的冲突
        for prop_key, values in all_properties.items():
            if len(set(str(v) for v in values)) > 1:  # 转换为字符串比较
                conflict = Conflict(
                    conflict_id=f"property_conflict_{entity_id}_{prop_key}",
                    conflict_type=ConflictType.PROPERTY_VALUE_CONFLICT,
                    description=f"实体 {entity_id} 的属性 {prop_key} 有冲突值",
                    conflicting_items=values,
                    confidence_scores=[1.0] * len(values)
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def detect_relation_conflicts(self, relations: List[Relation]) -> List[Conflict]:
        """检测关系冲突"""
        conflicts = []
        
        # 按实体对分组关系
        relation_groups = defaultdict(list)
        for relation in relations:
            key = (relation.head_entity_id, relation.tail_entity_id)
            relation_groups[key].append(relation)
        
        # 检查每组内的冲突
        for (head_id, tail_id), group in relation_groups.items():
            if len(group) <= 1:
                continue
            
            # 检测关系类型冲突
            types = [relation.type for relation in group]
            if len(set(types)) > 1:
                # 检查是否为矛盾关系
                if self._are_contradictory_relations(types):
                    conflict = Conflict(
                        conflict_id=f"contradictory_relations_{head_id}_{tail_id}",
                        conflict_type=ConflictType.CONTRADICTORY_RELATIONS,
                        description=f"实体 {head_id} 和 {tail_id} 之间存在矛盾关系",
                        conflicting_items=group,
                        confidence_scores=[getattr(rel, 'confidence', 1.0) for rel in group]
                    )
                    conflicts.append(conflict)
                else:
                    conflict = Conflict(
                        conflict_id=f"relation_type_conflict_{head_id}_{tail_id}",
                        conflict_type=ConflictType.RELATION_TYPE_CONFLICT,
                        description=f"实体 {head_id} 和 {tail_id} 之间有多种关系类型",
                        conflicting_items=types,
                        confidence_scores=[getattr(rel, 'confidence', 1.0) for rel in group]
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _are_contradictory_relations(self, relation_types: List[str]) -> bool:
        """判断关系类型是否矛盾"""
        # 定义矛盾关系对
        contradictory_pairs = {
            ('parent_of', 'child_of'),
            ('spouse_of', 'sibling_of'),
            ('works_for', 'competes_with'),
            ('located_in', 'not_located_in')
        }
        
        # 检查是否存在矛盾对
        type_set = set(relation_types)
        for pair in contradictory_pairs:
            if pair[0] in type_set and pair[1] in type_set:
                return True
            if pair[1] in type_set and pair[0] in type_set:
                return True
        
        return False
    
    def resolve_conflict(self, conflict: Conflict, strategy: str = None) -> Conflict:
        """解决冲突"""
        if not strategy:
            # 选择默认策略
            available_strategies = self.resolution_strategies.get(conflict.conflict_type, [])
            strategy = available_strategies[0] if available_strategies else 'highest_confidence'
        
        conflict.resolution_strategy = strategy
        
        try:
            if conflict.conflict_type == ConflictType.ENTITY_NAME_CONFLICT:
                conflict = self._resolve_name_conflict(conflict, strategy)
            
            elif conflict.conflict_type == ConflictType.ENTITY_TYPE_CONFLICT:
                conflict = self._resolve_type_conflict(conflict, strategy)
            
            elif conflict.conflict_type == ConflictType.PROPERTY_VALUE_CONFLICT:
                conflict = self._resolve_property_conflict(conflict, strategy)
            
            elif conflict.conflict_type == ConflictType.RELATION_TYPE_CONFLICT:
                conflict = self._resolve_relation_type_conflict(conflict, strategy)
            
            elif conflict.conflict_type == ConflictType.CONTRADICTORY_RELATIONS:
                conflict = self._resolve_contradictory_relations(conflict, strategy)
            
            else:
                # 默认使用最高置信度策略
                conflict = self._resolve_by_highest_confidence(conflict)
            
            # 记录解决历史
            self.conflict_history.append(conflict)
            
        except Exception as e:
            self.logger.error(f"解决冲突 {conflict.conflict_id} 时出错: {e}")
            conflict.resolved_value = conflict.conflicting_items[0]  # 默认选择第一个
            conflict.resolution_confidence = 0.1
        
        return conflict
    
    def _resolve_name_conflict(self, conflict: Conflict, strategy: str) -> Conflict:
        """解决名称冲突"""
        names = conflict.conflicting_items
        confidences = conflict.confidence_scores
        
        if strategy == 'highest_confidence':
            max_idx = confidences.index(max(confidences))
            conflict.resolved_value = names[max_idx]
            conflict.resolution_confidence = confidences[max_idx]
        
        elif strategy == 'most_frequent':
            name_counts = Counter(names)
            most_common = name_counts.most_common(1)[0]
            conflict.resolved_value = most_common[0]
            conflict.resolution_confidence = most_common[1] / len(names)
        
        elif strategy == 'longest_name':
            longest_name = max(names, key=len)
            conflict.resolved_value = longest_name
            conflict.resolution_confidence = 0.7  # 中等置信度
        
        else:
            # 默认策略
            conflict.resolved_value = names[0]
            conflict.resolution_confidence = 0.5
        
        return conflict
    
    def _resolve_type_conflict(self, conflict: Conflict, strategy: str) -> Conflict:
        """解决类型冲突"""
        types = conflict.conflicting_items
        confidences = conflict.confidence_scores
        
        if strategy == 'highest_confidence':
            max_idx = confidences.index(max(confidences))
            conflict.resolved_value = types[max_idx]
            conflict.resolution_confidence = confidences[max_idx]
        
        elif strategy == 'most_specific_type':
            # 选择最具体的类型（简化为最长的类型名）
            most_specific = max(types, key=len)
            conflict.resolved_value = most_specific
            conflict.resolution_confidence = 0.8
        
        elif strategy == 'vote':
            type_counts = Counter(types)
            most_common = type_counts.most_common(1)[0]
            conflict.resolved_value = most_common[0]
            conflict.resolution_confidence = most_common[1] / len(types)
        
        else:
            conflict.resolved_value = types[0]
            conflict.resolution_confidence = 0.5
        
        return conflict
    
    def _resolve_property_conflict(self, conflict: Conflict, strategy: str) -> Conflict:
        """解决属性值冲突"""
        values = conflict.conflicting_items
        confidences = conflict.confidence_scores
        
        if strategy == 'highest_confidence':
            max_idx = confidences.index(max(confidences))
            conflict.resolved_value = values[max_idx]
            conflict.resolution_confidence = confidences[max_idx]
        
        elif strategy == 'vote':
            value_counts = Counter(str(v) for v in values)
            most_common_str = value_counts.most_common(1)[0][0]
            
            # 找到对应的原始值
            for value in values:
                if str(value) == most_common_str:
                    conflict.resolved_value = value
                    break
            
            conflict.resolution_confidence = value_counts[most_common_str] / len(values)
        
        elif strategy == 'average_numeric':
            # 尝试计算数值平均值
            try:
                numeric_values = [float(v) for v in values]
                conflict.resolved_value = sum(numeric_values) / len(numeric_values)
                conflict.resolution_confidence = 0.8
            except (ValueError, TypeError):
                # 不是数值，回退到投票策略
                return self._resolve_property_conflict(conflict, 'vote')
        
        elif strategy == 'union_lists':
            # 合并列表值
            if all(isinstance(v, list) for v in values):
                merged = []
                for lst in values:
                    merged.extend(lst)
                conflict.resolved_value = list(set(merged))  # 去重
                conflict.resolution_confidence = 0.9
            else:
                return self._resolve_property_conflict(conflict, 'vote')
        
        else:
            conflict.resolved_value = values[0]
            conflict.resolution_confidence = 0.5
        
        return conflict
    
    def _resolve_relation_type_conflict(self, conflict: Conflict, strategy: str) -> Conflict:
        """解决关系类型冲突"""
        types = conflict.conflicting_items
        confidences = conflict.confidence_scores
        
        if strategy == 'highest_confidence':
            max_idx = confidences.index(max(confidences))
            conflict.resolved_value = types[max_idx]
            conflict.resolution_confidence = confidences[max_idx]
        
        elif strategy == 'most_frequent':
            type_counts = Counter(types)
            most_common = type_counts.most_common(1)[0]
            conflict.resolved_value = most_common[0]
            conflict.resolution_confidence = most_common[1] / len(types)
        
        else:
            conflict.resolved_value = types[0]
            conflict.resolution_confidence = 0.5
        
        return conflict
    
    def _resolve_contradictory_relations(self, conflict: Conflict, strategy: str) -> Conflict:
        """解决矛盾关系"""
        relations = conflict.conflicting_items
        confidences = conflict.confidence_scores
        
        if strategy == 'highest_confidence':
            max_idx = confidences.index(max(confidences))
            conflict.resolved_value = relations[max_idx]
            conflict.resolution_confidence = confidences[max_idx]
        
        elif strategy == 'source_authority':
            # 简化处理：选择第一个关系
            conflict.resolved_value = relations[0]
            conflict.resolution_confidence = 0.6
        
        else:
            conflict.resolved_value = relations[0]
            conflict.resolution_confidence = 0.5
        
        return conflict
    
    def _resolve_by_highest_confidence(self, conflict: Conflict) -> Conflict:
        """基于最高置信度解决冲突"""
        if not conflict.confidence_scores:
            conflict.resolved_value = conflict.conflicting_items[0] if conflict.conflicting_items else None
            conflict.resolution_confidence = 0.5
        else:
            max_idx = conflict.confidence_scores.index(max(conflict.confidence_scores))
            conflict.resolved_value = conflict.conflicting_items[max_idx]
            conflict.resolution_confidence = conflict.confidence_scores[max_idx]
        
        return conflict
    
    def batch_resolve_conflicts(self, conflicts: List[Conflict], 
                              strategy_mapping: Dict[ConflictType, str] = None) -> List[Conflict]:
        """批量解决冲突"""
        resolved_conflicts = []
        
        for conflict in conflicts:
            strategy = None
            if strategy_mapping and conflict.conflict_type in strategy_mapping:
                strategy = strategy_mapping[conflict.conflict_type]
            
            resolved_conflict = self.resolve_conflict(conflict, strategy)
            resolved_conflicts.append(resolved_conflict)
        
        return resolved_conflicts
    
    def get_conflict_statistics(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """获取冲突统计信息"""
        stats = {
            'total_conflicts': len(conflicts),
            'by_type': defaultdict(int),
            'resolved_count': 0,
            'high_confidence_resolutions': 0,  # > 0.8
            'average_resolution_confidence': 0.0
        }
        
        total_confidence = 0.0
        
        for conflict in conflicts:
            stats['by_type'][conflict.conflict_type.value] += 1
            
            if conflict.resolved_value is not None:
                stats['resolved_count'] += 1
                total_confidence += conflict.resolution_confidence
                
                if conflict.resolution_confidence > 0.8:
                    stats['high_confidence_resolutions'] += 1
        
        if stats['resolved_count'] > 0:
            stats['average_resolution_confidence'] = total_confidence / stats['resolved_count']
        
        return stats
    
    def generate_conflict_report(self, conflicts: List[Conflict]) -> str:
        """生成冲突报告"""
        stats = self.get_conflict_statistics(conflicts)
        
        report = f"冲突解决报告\n"
        report += f"=" * 50 + "\n"
        report += f"总冲突数: {stats['total_conflicts']}\n"
        report += f"已解决: {stats['resolved_count']}\n"
        report += f"平均解决置信度: {stats['average_resolution_confidence']:.2f}\n"
        report += f"高置信度解决: {stats['high_confidence_resolutions']}\n\n"
        
        report += f"按类型分布:\n"
        for conflict_type, count in stats['by_type'].items():
            report += f"  {conflict_type}: {count}\n"
        
        # 添加具体冲突示例
        report += f"\n冲突示例:\n"
        for i, conflict in enumerate(conflicts[:5]):
            status = "已解决" if conflict.resolved_value is not None else "未解决"
            report += f"  {i+1}. {conflict.description} - {status}\n"
            if conflict.resolved_value is not None:
                report += f"     解决方案: {conflict.resolved_value} (置信度: {conflict.resolution_confidence:.2f})\n"
        
        return report
    
    def print_conflict_summary(self, conflicts: List[Conflict]):
        """打印冲突摘要"""
        print(self.generate_conflict_report(conflicts))