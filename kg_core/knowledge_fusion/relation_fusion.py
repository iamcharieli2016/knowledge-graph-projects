"""
关系融合模块 - 合并和去重关系信息
"""
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import uuid
from ..entity_definition.relation_types import Relation
from ..knowledge_mapping.similarity_calculator import SimilarityCalculator


@dataclass
class RelationCluster:
    """关系聚类"""
    cluster_id: str
    relations: List[Relation]
    representative_relation: Optional[Relation] = None
    confidence: float = 0.0
    fusion_method: str = ""


@dataclass
class RelationFusionResult:
    """关系融合结果"""
    fused_relation: Relation
    source_relations: List[Relation]
    confidence: float
    fusion_evidence: Dict[str, any] = field(default_factory=dict)


class RelationFusion:
    """关系融合器"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.similarity_calculator = SimilarityCalculator()
        self.fusion_rules = self._build_fusion_rules()
    
    def _build_fusion_rules(self) -> Dict[str, Dict[str, any]]:
        """构建关系融合规则"""
        rules = {
            'relation_matching': {
                'exact_match_weight': 1.0,
                'type_match_weight': 0.6,
                'entity_match_weight': 0.8,
                'context_match_weight': 0.4
            },
            'confidence_fusion': {
                'strategy': 'weighted_average',  # max, average, weighted_average
                'source_weight_factor': 0.3,
                'frequency_weight_factor': 0.4,
                'quality_weight_factor': 0.3
            },
            'property_fusion': {
                'merge_strategy': 'union',  # union, intersection, vote
                'conflict_resolution': 'highest_confidence'
            },
            'duplicate_handling': {
                'keep_all_sources': True,
                'preserve_provenance': True
            }
        }
        return rules
    
    def identify_duplicate_relations(self, relations: List[Relation]) -> List[List[int]]:
        """识别重复关系"""
        if len(relations) <= 1:
            return []
        
        duplicates = []
        visited = set()
        
        for i in range(len(relations)):
            if i in visited:
                continue
            
            duplicate_group = [i]
            
            for j in range(i + 1, len(relations)):
                if j in visited:
                    continue
                
                if self._are_duplicate_relations(relations[i], relations[j]):
                    duplicate_group.append(j)
                    visited.add(j)
            
            if len(duplicate_group) > 1:
                duplicates.append(duplicate_group)
            
            visited.add(i)
        
        return duplicates
    
    def _are_duplicate_relations(self, relation1: Relation, relation2: Relation) -> bool:
        """判断两个关系是否重复"""
        # 精确匹配：类型、头实体、尾实体都相同
        if (relation1.type == relation2.type and 
            relation1.head_entity_id == relation2.head_entity_id and
            relation1.tail_entity_id == relation2.tail_entity_id):
            return True
        
        # 计算综合相似度
        similarity = self._calculate_relation_similarity(relation1, relation2)
        return similarity >= self.similarity_threshold
    
    def _calculate_relation_similarity(self, relation1: Relation, relation2: Relation) -> float:
        """计算关系相似度"""
        similarities = []
        weights = self.fusion_rules['relation_matching']
        
        # 类型相似度
        type_sim = 1.0 if relation1.type == relation2.type else 0.0
        similarities.append(('type', type_sim, weights['type_match_weight']))
        
        # 实体匹配相似度
        entity_sim = 0.0
        if (relation1.head_entity_id == relation2.head_entity_id and
            relation1.tail_entity_id == relation2.tail_entity_id):
            entity_sim = 1.0
        elif (relation1.head_entity_id == relation2.tail_entity_id and
              relation1.tail_entity_id == relation2.head_entity_id):
            # 考虑反向关系
            entity_sim = 0.8
        
        similarities.append(('entity', entity_sim, weights['entity_match_weight']))
        
        # 上下文相似度（如果有的话）
        context_sim = 0.0
        if (relation1.properties and relation2.properties and
            'context' in relation1.properties and 'context' in relation2.properties):
            context_sim = self.similarity_calculator.context_similarity(
                relation1.properties['context'],
                relation2.properties['context']
            )
        
        similarities.append(('context', context_sim, weights['context_match_weight']))
        
        # 加权平均
        total_weight = sum(weight for _, _, weight in similarities)
        weighted_sum = sum(sim * weight for _, sim, weight in similarities)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def cluster_relations(self, relations: List[Relation]) -> List[RelationCluster]:
        """聚类关系"""
        duplicate_groups = self.identify_duplicate_relations(relations)
        clusters = []
        
        # 为每个重复组创建聚类
        for group_indices in duplicate_groups:
            group_relations = [relations[i] for i in group_indices]
            
            cluster = RelationCluster(
                cluster_id=str(uuid.uuid4()),
                relations=group_relations,
                confidence=self._calculate_cluster_confidence(group_relations),
                fusion_method="similarity_based"
            )
            
            # 选择代表关系
            cluster.representative_relation = self._select_representative_relation(group_relations)
            clusters.append(cluster)
        
        # 为未聚类的关系创建单独的聚类
        clustered_indices = set()
        for group in duplicate_groups:
            clustered_indices.update(group)
        
        for i, relation in enumerate(relations):
            if i not in clustered_indices:
                cluster = RelationCluster(
                    cluster_id=str(uuid.uuid4()),
                    relations=[relation],
                    representative_relation=relation,
                    confidence=1.0,
                    fusion_method="single_relation"
                )
                clusters.append(cluster)
        
        return clusters
    
    def _calculate_cluster_confidence(self, relations: List[Relation]) -> float:
        """计算关系聚类置信度"""
        if len(relations) == 1:
            return relations[0].confidence if hasattr(relations[0], 'confidence') else 1.0
        
        # 计算关系间平均相似度
        total_similarity = 0.0
        comparisons = 0
        
        for i in range(len(relations)):
            for j in range(i + 1, len(relations)):
                similarity = self._calculate_relation_similarity(relations[i], relations[j])
                total_similarity += similarity
                comparisons += 1
        
        avg_similarity = total_similarity / comparisons if comparisons > 0 else 0.0
        
        # 结合个体置信度
        individual_confidences = [
            getattr(rel, 'confidence', 1.0) for rel in relations
        ]
        avg_individual_confidence = sum(individual_confidences) / len(individual_confidences)
        
        # 综合置信度
        return (avg_similarity * 0.6 + avg_individual_confidence * 0.4)
    
    def _select_representative_relation(self, relations: List[Relation]) -> Relation:
        """选择代表关系"""
        if len(relations) == 1:
            return relations[0]
        
        # 评分标准
        scores = []
        
        for relation in relations:
            score = 0.0
            
            # 基础置信度
            base_confidence = getattr(relation, 'confidence', 1.0)
            score += base_confidence * 0.5
            
            # 属性完整性
            if relation.properties:
                score += len(relation.properties) * 0.1
            
            # 来源质量（如果有标记）
            if relation.properties and 'source_quality' in relation.properties:
                score += relation.properties['source_quality'] * 0.3
            
            # 新鲜度（如果有时间戳）
            if relation.properties and 'timestamp' in relation.properties:
                # 简化处理，假设更新的关系得分更高
                score += 0.1
            
            scores.append((relation, score))
        
        # 选择得分最高的关系
        best_relation = max(scores, key=lambda x: x[1])[0]
        return best_relation
    
    def fuse_relation_cluster(self, cluster: RelationCluster) -> RelationFusionResult:
        """融合关系聚类"""
        if len(cluster.relations) == 1:
            # 单个关系无需融合
            return RelationFusionResult(
                fused_relation=cluster.relations[0],
                source_relations=cluster.relations,
                confidence=cluster.confidence,
                fusion_evidence={'method': 'no_fusion_needed'}
            )
        
        # 创建融合后的关系
        fused_relation = self._create_fused_relation(cluster.relations)
        
        # 计算融合置信度
        fusion_confidence = self._calculate_fusion_confidence(cluster.relations)
        
        return RelationFusionResult(
            fused_relation=fused_relation,
            source_relations=cluster.relations,
            confidence=fusion_confidence,
            fusion_evidence={
                'method': 'multi_relation_fusion',
                'source_count': len(cluster.relations),
                'cluster_confidence': cluster.confidence
            }
        )
    
    def _create_fused_relation(self, relations: List[Relation]) -> Relation:
        """创建融合后的关系"""
        # 选择代表关系作为基础
        representative = self._select_representative_relation(relations)
        
        # 融合置信度
        fused_confidence = self._calculate_fusion_confidence(relations)
        
        # 融合属性
        fused_properties = self._fuse_relation_properties(
            [rel.properties for rel in relations if rel.properties]
        )
        
        # 添加融合信息
        fused_properties['fusion_info'] = {
            'source_count': len(relations),
            'source_ids': [rel.id for rel in relations],
            'fusion_timestamp': str(uuid.uuid4())  # 简化的时间戳
        }
        
        # 创建新的关系ID
        fused_id = str(uuid.uuid4())
        
        return Relation(
            id=fused_id,
            type=representative.type,
            head_entity_id=representative.head_entity_id,
            tail_entity_id=representative.tail_entity_id,
            properties=fused_properties,
            confidence=fused_confidence
        )
    
    def _calculate_fusion_confidence(self, relations: List[Relation]) -> float:
        """计算融合置信度"""
        strategy = self.fusion_rules['confidence_fusion']['strategy']
        
        confidences = [getattr(rel, 'confidence', 1.0) for rel in relations]
        
        if strategy == 'max':
            return max(confidences)
        
        elif strategy == 'average':
            return sum(confidences) / len(confidences)
        
        elif strategy == 'weighted_average':
            # 考虑来源数量的加权
            source_weight = min(1.0, len(relations) / 5.0)  # 5个来源达到最高权重
            avg_confidence = sum(confidences) / len(confidences)
            
            return min(1.0, avg_confidence * (1.0 + source_weight * 0.2))
        
        else:
            return sum(confidences) / len(confidences)
    
    def _fuse_relation_properties(self, property_lists: List[Dict[str, any]]) -> Dict[str, any]:
        """融合关系属性"""
        if not property_lists:
            return {}
        
        strategy = self.fusion_rules['property_fusion']['merge_strategy']
        fused_properties = {}
        
        # 收集所有属性键
        all_keys = set()
        for props in property_lists:
            if props:
                all_keys.update(props.keys())
        
        # 为每个属性键融合值
        for key in all_keys:
            values = []
            for props in property_lists:
                if props and key in props:
                    values.append(props[key])
            
            if values:
                if strategy == 'union':
                    fused_properties[key] = self._merge_property_values_union(values)
                elif strategy == 'intersection':
                    fused_properties[key] = self._merge_property_values_intersection(values)
                elif strategy == 'vote':
                    fused_properties[key] = self._merge_property_values_vote(values)
                else:
                    fused_properties[key] = values[0]  # 默认取第一个
        
        return fused_properties
    
    def _merge_property_values_union(self, values: List[any]) -> any:
        """合并属性值（并集）"""
        if len(values) == 1:
            return values[0]
        
        if all(isinstance(v, list) for v in values):
            # 合并列表
            merged = []
            for lst in values:
                merged.extend(lst)
            return list(set(merged))  # 去重
        
        elif all(isinstance(v, str) for v in values):
            # 对于字符串，返回最长的或最完整的
            return max(values, key=len)
        
        else:
            # 其他类型，返回最常见的值
            value_counts = {}
            for value in values:
                str_value = str(value)
                value_counts[str_value] = value_counts.get(str_value, 0) + 1
            
            most_common_str = max(value_counts.items(), key=lambda x: x[1])[0]
            
            for value in values:
                if str(value) == most_common_str:
                    return value
            
            return values[0]
    
    def _merge_property_values_intersection(self, values: List[any]) -> any:
        """合并属性值（交集）"""
        if len(values) == 1:
            return values[0]
        
        if all(isinstance(v, list) for v in values):
            # 计算列表交集
            result = set(values[0])
            for lst in values[1:]:
                result &= set(lst)
            return list(result)
        
        else:
            # 非列表类型，检查是否所有值都相同
            if len(set(str(v) for v in values)) == 1:
                return values[0]
            else:
                return None  # 没有交集
    
    def _merge_property_values_vote(self, values: List[any]) -> any:
        """合并属性值（投票）"""
        value_counts = {}
        for value in values:
            str_value = str(value)
            value_counts[str_value] = value_counts.get(str_value, 0) + 1
        
        most_common_str = max(value_counts.items(), key=lambda x: x[1])[0]
        
        for value in values:
            if str(value) == most_common_str:
                return value
        
        return values[0]
    
    def remove_redundant_relations(self, relations: List[Relation]) -> List[Relation]:
        """移除冗余关系"""
        if len(relations) <= 1:
            return relations
        
        # 按实体对分组
        entity_pair_groups = defaultdict(list)
        
        for relation in relations:
            key = (relation.head_entity_id, relation.tail_entity_id)
            entity_pair_groups[key].append(relation)
        
        # 对每组保留最佳关系
        filtered_relations = []
        
        for group in entity_pair_groups.values():
            if len(group) == 1:
                filtered_relations.extend(group)
            else:
                # 按关系类型分组
                type_groups = defaultdict(list)
                for rel in group:
                    type_groups[rel.type].append(rel)
                
                # 每种关系类型保留置信度最高的
                for type_group in type_groups.values():
                    best_relation = max(type_group, 
                                      key=lambda x: getattr(x, 'confidence', 1.0))
                    filtered_relations.append(best_relation)
        
        return filtered_relations
    
    def batch_fuse_relations(self, relations: List[Relation]) -> List[RelationFusionResult]:
        """批量融合关系"""
        # 聚类关系
        clusters = self.cluster_relations(relations)
        
        # 融合每个聚类
        fusion_results = []
        for cluster in clusters:
            result = self.fuse_relation_cluster(cluster)
            fusion_results.append(result)
        
        return fusion_results
    
    def get_fusion_statistics(self, fusion_results: List[RelationFusionResult]) -> Dict[str, any]:
        """获取融合统计信息"""
        stats = {
            'total_fusions': len(fusion_results),
            'single_relation_count': 0,
            'multi_relation_count': 0,
            'average_confidence': 0.0,
            'high_confidence_count': 0,  # > 0.8
            'source_distribution': defaultdict(int),
            'relation_type_distribution': defaultdict(int)
        }
        
        total_confidence = 0.0
        
        for result in fusion_results:
            source_count = len(result.source_relations)
            
            if source_count == 1:
                stats['single_relation_count'] += 1
            else:
                stats['multi_relation_count'] += 1
            
            stats['source_distribution'][source_count] += 1
            stats['relation_type_distribution'][result.fused_relation.type] += 1
            
            total_confidence += result.confidence
            
            if result.confidence > 0.8:
                stats['high_confidence_count'] += 1
        
        if fusion_results:
            stats['average_confidence'] = total_confidence / len(fusion_results)
        
        return stats
    
    def print_fusion_results(self, fusion_results: List[RelationFusionResult]):
        """打印关系融合结果"""
        stats = self.get_fusion_statistics(fusion_results)
        
        print(f"关系融合结果 ({stats['total_fusions']} 个融合关系):")
        print(f"  单关系: {stats['single_relation_count']}")
        print(f"  多关系融合: {stats['multi_relation_count']}")
        print(f"  平均置信度: {stats['average_confidence']:.2f}")
        print(f"  高置信度融合: {stats['high_confidence_count']}")
        
        print(f"\n源分布:")
        for source_count, count in sorted(stats['source_distribution'].items()):
            print(f"  {source_count}个源: {count}个融合")
        
        print(f"\n关系类型分布:")
        for rel_type, count in sorted(stats['relation_type_distribution'].items(), 
                                    key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {rel_type}: {count}")
        
        # 显示一些具体的融合示例
        print(f"\n融合示例:")
        for i, result in enumerate(fusion_results[:5]):
            rel = result.fused_relation
            source_count = len(result.source_relations)
            print(f"  {rel.head_entity_id} -[{rel.type}]-> {rel.tail_entity_id} "
                  f"(来源: {source_count}, 置信度: {result.confidence:.2f})")