"""
实体融合模块 - 合并来自不同源的实体信息
"""
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import uuid
from ..entity_definition.entity_types import Entity
from ..knowledge_mapping.similarity_calculator import SimilarityCalculator


@dataclass
class EntityCluster:
    """实体聚类"""
    cluster_id: str
    entities: List[Entity]
    representative_entity: Optional[Entity] = None
    confidence: float = 0.0
    fusion_method: str = ""


@dataclass
class FusionResult:
    """融合结果"""
    fused_entity: Entity
    source_entities: List[Entity]
    confidence: float
    fusion_evidence: Dict[str, any] = field(default_factory=dict)


class EntityFusion:
    """实体融合器"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.similarity_calculator = SimilarityCalculator()
        self.fusion_rules = self._build_fusion_rules()
    
    def _build_fusion_rules(self) -> Dict[str, Dict[str, any]]:
        """构建融合规则"""
        rules = {
            'name_selection': {
                'priority_sources': ['manual', 'high_confidence', 'frequent'],
                'prefer_longer': True,
                'avoid_abbreviations': True
            },
            'property_fusion': {
                'conflict_resolution': 'vote',  # vote, latest, confidence_based
                'merge_lists': True,
                'deduplicate': True
            },
            'type_resolution': {
                'strategy': 'most_specific',  # most_specific, vote, confidence_based
                'hierarchy_aware': True
            },
            'confidence_calculation': {
                'base_weight': 0.5,
                'source_weight': 0.3,
                'similarity_weight': 0.2
            }
        }
        return rules
    
    def identify_duplicate_entities(self, entities: List[Entity]) -> List[List[int]]:
        """识别重复实体"""
        if len(entities) <= 1:
            return []
        
        # 构建实体信息字典用于相似度计算
        entity_dicts = []
        for entity in entities:
            entity_dict = {
                'name': entity.name,
                'type': entity.type,
                'properties': entity.properties,
                'aliases': entity.aliases or []
            }
            entity_dicts.append(entity_dict)
        
        # 计算相似度并找出重复项
        duplicates = []
        visited = set()
        
        for i in range(len(entities)):
            if i in visited:
                continue
            
            duplicate_group = [i]
            
            for j in range(i + 1, len(entities)):
                if j in visited:
                    continue
                
                similarity = self.similarity_calculator.entity_similarity(
                    entity_dicts[i], entity_dicts[j]
                )
                
                if similarity >= self.similarity_threshold:
                    duplicate_group.append(j)
                    visited.add(j)
            
            if len(duplicate_group) > 1:
                duplicates.append(duplicate_group)
            
            visited.add(i)
        
        return duplicates
    
    def cluster_entities(self, entities: List[Entity]) -> List[EntityCluster]:
        """聚类实体"""
        duplicate_groups = self.identify_duplicate_entities(entities)
        clusters = []
        
        # 为每个重复组创建聚类
        for group_indices in duplicate_groups:
            group_entities = [entities[i] for i in group_indices]
            
            cluster = EntityCluster(
                cluster_id=str(uuid.uuid4()),
                entities=group_entities,
                confidence=self._calculate_cluster_confidence(group_entities),
                fusion_method="similarity_based"
            )
            
            # 选择代表实体
            cluster.representative_entity = self._select_representative_entity(group_entities)
            clusters.append(cluster)
        
        # 为未聚类的实体创建单独的聚类
        clustered_indices = set()
        for group in duplicate_groups:
            clustered_indices.update(group)
        
        for i, entity in enumerate(entities):
            if i not in clustered_indices:
                cluster = EntityCluster(
                    cluster_id=str(uuid.uuid4()),
                    entities=[entity],
                    representative_entity=entity,
                    confidence=1.0,
                    fusion_method="single_entity"
                )
                clusters.append(cluster)
        
        return clusters
    
    def _calculate_cluster_confidence(self, entities: List[Entity]) -> float:
        """计算聚类置信度"""
        if len(entities) == 1:
            return 1.0
        
        # 计算实体间平均相似度
        total_similarity = 0.0
        comparisons = 0
        
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity_dict1 = {
                    'name': entities[i].name,
                    'type': entities[i].type,
                    'properties': entities[i].properties,
                    'aliases': entities[i].aliases or []
                }
                entity_dict2 = {
                    'name': entities[j].name,
                    'type': entities[j].type,
                    'properties': entities[j].properties,
                    'aliases': entities[j].aliases or []
                }
                
                similarity = self.similarity_calculator.entity_similarity(
                    entity_dict1, entity_dict2
                )
                total_similarity += similarity
                comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0.0
    
    def _select_representative_entity(self, entities: List[Entity]) -> Entity:
        """选择代表实体"""
        if len(entities) == 1:
            return entities[0]
        
        # 评分标准
        scores = []
        
        for entity in entities:
            score = 0.0
            
            # 名称长度评分（更长的名称可能更完整）
            if self.fusion_rules['name_selection']['prefer_longer']:
                score += len(entity.name) * 0.1
            
            # 属性完整性评分
            if entity.properties:
                score += len(entity.properties) * 0.2
            
            # 别名数量评分
            if entity.aliases:
                score += len(entity.aliases) * 0.1
            
            # 来源置信度评分（如果有的话）
            if 'confidence' in entity.properties:
                score += float(entity.properties.get('confidence', 0)) * 0.5
            
            scores.append((entity, score))
        
        # 选择得分最高的实体
        best_entity = max(scores, key=lambda x: x[1])[0]
        return best_entity
    
    def fuse_entity_cluster(self, cluster: EntityCluster) -> FusionResult:
        """融合实体聚类"""
        if len(cluster.entities) == 1:
            # 单个实体无需融合
            return FusionResult(
                fused_entity=cluster.entities[0],
                source_entities=cluster.entities,
                confidence=1.0,
                fusion_evidence={'method': 'no_fusion_needed'}
            )
        
        # 创建融合后的实体
        fused_entity = self._create_fused_entity(cluster.entities)
        
        # 计算融合置信度
        fusion_confidence = self._calculate_fusion_confidence(cluster.entities, fused_entity)
        
        return FusionResult(
            fused_entity=fused_entity,
            source_entities=cluster.entities,
            confidence=fusion_confidence,
            fusion_evidence={
                'method': 'multi_entity_fusion',
                'source_count': len(cluster.entities),
                'cluster_confidence': cluster.confidence
            }
        )
    
    def _create_fused_entity(self, entities: List[Entity]) -> Entity:
        """创建融合后的实体"""
        # 选择最佳名称
        fused_name = self._fuse_names([entity.name for entity in entities])
        
        # 确定实体类型
        fused_type = self._fuse_types([entity.type for entity in entities])
        
        # 融合属性
        fused_properties = self._fuse_properties([entity.properties for entity in entities])
        
        # 收集所有别名
        all_aliases = []
        for entity in entities:
            if entity.aliases:
                all_aliases.extend(entity.aliases)
            # 将非主要名称也作为别名
            if entity.name != fused_name:
                all_aliases.append(entity.name)
        
        # 去重别名
        fused_aliases = list(set(all_aliases))
        
        # 创建新的实体ID
        fused_id = str(uuid.uuid4())
        
        return Entity(
            id=fused_id,
            name=fused_name,
            type=fused_type,
            properties=fused_properties,
            aliases=fused_aliases
        )
    
    def _fuse_names(self, names: List[str]) -> str:
        """融合实体名称"""
        if not names:
            return ""
        
        # 去重
        unique_names = list(set(names))
        
        if len(unique_names) == 1:
            return unique_names[0]
        
        # 选择最长的非缩写名称
        if self.fusion_rules['name_selection']['prefer_longer']:
            # 过滤掉明显的缩写（全大写且较短）
            non_abbrev_names = [
                name for name in unique_names 
                if not (name.isupper() and len(name) <= 5)
            ]
            
            if non_abbrev_names:
                return max(non_abbrev_names, key=len)
        
        # 选择最常见的名称
        name_counts = {name: names.count(name) for name in unique_names}
        return max(name_counts.items(), key=lambda x: x[1])[0]
    
    def _fuse_types(self, types: List[str]) -> str:
        """融合实体类型"""
        if not types:
            return "Unknown"
        
        # 去重并统计
        type_counts = {}
        for entity_type in types:
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        strategy = self.fusion_rules['type_resolution']['strategy']
        
        if strategy == 'vote':
            # 投票决定
            return max(type_counts.items(), key=lambda x: x[1])[0]
        
        elif strategy == 'most_specific':
            # 选择最具体的类型（这里简化为选择最长的类型名）
            return max(type_counts.keys(), key=len)
        
        else:
            # 默认投票
            return max(type_counts.items(), key=lambda x: x[1])[0]
    
    def _fuse_properties(self, property_lists: List[Dict[str, any]]) -> Dict[str, any]:
        """融合实体属性"""
        if not property_lists:
            return {}
        
        fused_properties = {}
        all_keys = set()
        
        # 收集所有属性键
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
                fused_properties[key] = self._fuse_property_values(key, values)
        
        return fused_properties
    
    def _fuse_property_values(self, property_name: str, values: List[any]) -> any:
        """融合属性值"""
        if not values:
            return None
        
        if len(values) == 1:
            return values[0]
        
        # 处理不同类型的值
        if all(isinstance(v, str) for v in values):
            return self._fuse_string_values(values)
        
        elif all(isinstance(v, (int, float)) for v in values):
            return self._fuse_numeric_values(values)
        
        elif all(isinstance(v, list) for v in values):
            return self._fuse_list_values(values)
        
        else:
            # 混合类型，选择最常见的值
            value_counts = {}
            for value in values:
                str_value = str(value)
                value_counts[str_value] = value_counts.get(str_value, 0) + 1
            
            most_common_str = max(value_counts.items(), key=lambda x: x[1])[0]
            
            # 返回原始类型的值
            for value in values:
                if str(value) == most_common_str:
                    return value
            
            return values[0]  # 备选方案
    
    def _fuse_string_values(self, values: List[str]) -> str:
        """融合字符串值"""
        # 去重
        unique_values = list(set(values))
        
        if len(unique_values) == 1:
            return unique_values[0]
        
        # 选择最常见的值
        value_counts = {value: values.count(value) for value in unique_values}
        return max(value_counts.items(), key=lambda x: x[1])[0]
    
    def _fuse_numeric_values(self, values: List[float]) -> float:
        """融合数值"""
        # 计算平均值
        return sum(values) / len(values)
    
    def _fuse_list_values(self, values: List[List]) -> List:
        """融合列表值"""
        if self.fusion_rules['property_fusion']['merge_lists']:
            # 合并所有列表
            merged = []
            for lst in values:
                merged.extend(lst)
            
            if self.fusion_rules['property_fusion']['deduplicate']:
                # 去重（保持顺序）
                seen = set()
                deduped = []
                for item in merged:
                    if item not in seen:
                        seen.add(item)
                        deduped.append(item)
                return deduped
            else:
                return merged
        else:
            # 选择最长的列表
            return max(values, key=len)
    
    def _calculate_fusion_confidence(self, source_entities: List[Entity], 
                                   fused_entity: Entity) -> float:
        """计算融合置信度"""
        if len(source_entities) == 1:
            return 1.0
        
        confidence_factors = []
        
        # 源实体数量因子（更多源可能意味着更高置信度）
        source_factor = min(1.0, len(source_entities) / 5.0)  # 5个源达到最高分
        confidence_factors.append(('source_count', source_factor, 0.3))
        
        # 属性完整性因子
        total_props = sum(len(entity.properties) for entity in source_entities)
        fused_props = len(fused_entity.properties)
        completeness_factor = fused_props / total_props if total_props > 0 else 0.5
        confidence_factors.append(('completeness', completeness_factor, 0.4))
        
        # 一致性因子（名称和类型的一致性）
        name_consistency = len(set(entity.name for entity in source_entities)) == 1
        type_consistency = len(set(entity.type for entity in source_entities)) == 1
        consistency_factor = (name_consistency + type_consistency) / 2
        confidence_factors.append(('consistency', consistency_factor, 0.3))
        
        # 加权平均
        weighted_sum = sum(factor * weight for _, factor, weight in confidence_factors)
        return min(weighted_sum, 1.0)
    
    def batch_fuse_entities(self, entities: List[Entity]) -> List[FusionResult]:
        """批量融合实体"""
        # 聚类实体
        clusters = self.cluster_entities(entities)
        
        # 融合每个聚类
        fusion_results = []
        for cluster in clusters:
            result = self.fuse_entity_cluster(cluster)
            fusion_results.append(result)
        
        return fusion_results
    
    def get_fusion_statistics(self, fusion_results: List[FusionResult]) -> Dict[str, any]:
        """获取融合统计信息"""
        stats = {
            'total_fusions': len(fusion_results),
            'single_entity_count': 0,
            'multi_entity_count': 0,
            'average_confidence': 0.0,
            'high_confidence_count': 0,  # > 0.8
            'source_distribution': defaultdict(int)
        }
        
        total_confidence = 0.0
        
        for result in fusion_results:
            source_count = len(result.source_entities)
            
            if source_count == 1:
                stats['single_entity_count'] += 1
            else:
                stats['multi_entity_count'] += 1
            
            stats['source_distribution'][source_count] += 1
            
            total_confidence += result.confidence
            
            if result.confidence > 0.8:
                stats['high_confidence_count'] += 1
        
        if fusion_results:
            stats['average_confidence'] = total_confidence / len(fusion_results)
        
        return stats
    
    def print_fusion_results(self, fusion_results: List[FusionResult]):
        """打印融合结果"""
        stats = self.get_fusion_statistics(fusion_results)
        
        print(f"实体融合结果 ({stats['total_fusions']} 个融合实体):")
        print(f"  单实体: {stats['single_entity_count']}")
        print(f"  多实体融合: {stats['multi_entity_count']}")
        print(f"  平均置信度: {stats['average_confidence']:.2f}")
        print(f"  高置信度融合: {stats['high_confidence_count']}")
        
        print(f"\n源分布:")
        for source_count, count in sorted(stats['source_distribution'].items()):
            print(f"  {source_count}个源: {count}个融合")
        
        # 显示一些具体的融合示例
        print(f"\n融合示例:")
        for i, result in enumerate(fusion_results[:5]):
            source_names = [entity.name for entity in result.source_entities]
            print(f"  {result.fused_entity.name} <- {', '.join(source_names)} "
                  f"(置信度: {result.confidence:.2f})")