"""
实体映射模块 - 将抽取的实体映射到本体中的标准实体
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re
from Levenshtein import distance as levenshtein_distance
from ..knowledge_extraction.entity_extractor import ExtractedEntity
from ..entity_definition.entity_types import Entity


@dataclass
class EntityMapping:
    """实体映射结果"""
    extracted_entity: ExtractedEntity
    mapped_entity: Optional[Entity]
    confidence: float
    mapping_type: str  # 'exact', 'fuzzy', 'new', 'alias'
    similarity_score: float = 0.0


class EntityMapper:
    """实体映射器"""
    
    def __init__(self):
        self.known_entities: Dict[str, Entity] = {}
        self.entity_aliases: Dict[str, List[str]] = {}
        self.similarity_threshold = 0.8
        self.name_normalization_rules = self._build_normalization_rules()
    
    def _build_normalization_rules(self) -> List[Tuple[str, str]]:
        """构建名称规范化规则"""
        rules = [
            # 去除常见后缀
            (r'公司$', ''),
            (r'有限公司$', ''),
            (r'股份有限公司$', ''),
            (r'集团$', ''),
            (r'企业$', ''),
            
            # 去除常见前缀
            (r'^中国', ''),
            (r'^北京', ''),
            (r'^上海', ''),
            
            # 统一空格
            (r'\s+', ''),
            
            # 统一括号内容
            (r'\([^)]*\)', ''),
            (r'（[^）]*）', ''),
        ]
        return rules
    
    def normalize_entity_name(self, name: str) -> str:
        """规范化实体名称"""
        normalized = name.strip()
        
        for pattern, replacement in self.name_normalization_rules:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized.strip()
    
    def add_known_entity(self, entity: Entity):
        """添加已知实体"""
        self.known_entities[entity.id] = entity
        
        # 添加名称映射
        normalized_name = self.normalize_entity_name(entity.name)
        self.known_entities[normalized_name] = entity
        
        # 添加别名映射
        if entity.aliases:
            for alias in entity.aliases:
                if entity.id not in self.entity_aliases:
                    self.entity_aliases[entity.id] = []
                self.entity_aliases[entity.id].append(alias)
    
    def exact_match(self, extracted_entity: ExtractedEntity) -> Optional[Entity]:
        """精确匹配"""
        # 尝试原始名称匹配
        if extracted_entity.text in self.known_entities:
            return self.known_entities[extracted_entity.text]
        
        # 尝试规范化名称匹配
        normalized_name = self.normalize_entity_name(extracted_entity.text)
        if normalized_name in self.known_entities:
            return self.known_entities[normalized_name]
        
        # 尝试别名匹配
        for entity_id, aliases in self.entity_aliases.items():
            if extracted_entity.text in aliases:
                return self.known_entities[entity_id]
        
        return None
    
    def fuzzy_match(self, extracted_entity: ExtractedEntity) -> List[Tuple[Entity, float]]:
        """模糊匹配"""
        candidates = []
        query_name = self.normalize_entity_name(extracted_entity.text)
        
        for entity in self.known_entities.values():
            if isinstance(entity, str):  # 跳过字符串键
                continue
            
            # 计算与实体名称的相似度
            target_name = self.normalize_entity_name(entity.name)
            similarity = self._calculate_string_similarity(query_name, target_name)
            
            if similarity > self.similarity_threshold:
                candidates.append((entity, similarity))
            
            # 计算与别名的相似度
            if entity.aliases:
                for alias in entity.aliases:
                    alias_normalized = self.normalize_entity_name(alias)
                    alias_similarity = self._calculate_string_similarity(query_name, alias_normalized)
                    if alias_similarity > self.similarity_threshold:
                        candidates.append((entity, alias_similarity))
        
        # 按相似度排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        if not str1 or not str2:
            return 0.0
        
        # Levenshtein距离相似度
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0
        
        lev_similarity = 1.0 - (levenshtein_distance(str1, str2) / max_len)
        
        # Jaccard相似度（字符级别）
        set1 = set(str1)
        set2 = set(str2)
        jaccard_similarity = len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0.0
        
        # 最长公共子序列相似度（简化版）
        lcs_len = self._lcs_length(str1, str2)
        lcs_similarity = (2.0 * lcs_len) / (len(str1) + len(str2)) if (len(str1) + len(str2)) > 0 else 0.0
        
        # 综合相似度
        combined_similarity = (lev_similarity * 0.5 + jaccard_similarity * 0.3 + lcs_similarity * 0.2)
        
        return combined_similarity
    
    def _lcs_length(self, str1: str, str2: str) -> int:
        """计算最长公共子序列长度"""
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def semantic_match(self, extracted_entity: ExtractedEntity) -> List[Tuple[Entity, float]]:
        """语义匹配（简化版，实际可以使用向量相似度）"""
        candidates = []
        
        # 基于实体类型的语义匹配
        for entity in self.known_entities.values():
            if isinstance(entity, str):
                continue
            
            if entity.type == extracted_entity.type:
                # 同类型实体获得基础分数
                base_score = 0.6
                
                # 基于属性的语义相似度
                semantic_score = self._calculate_semantic_similarity(extracted_entity, entity)
                
                final_score = base_score + semantic_score * 0.4
                
                if final_score > 0.7:
                    candidates.append((entity, final_score))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def _calculate_semantic_similarity(self, extracted_entity: ExtractedEntity, known_entity: Entity) -> float:
        """计算语义相似度"""
        similarity = 0.0
        
        # 基于上下文的相似度（简化版）
        if hasattr(extracted_entity, 'context') and extracted_entity.context:
            context_words = set(extracted_entity.context.lower().split())
            
            # 检查已知实体的属性是否在上下文中出现
            for prop_value in known_entity.properties.values():
                if isinstance(prop_value, str):
                    prop_words = set(prop_value.lower().split())
                    if context_words & prop_words:
                        similarity += 0.2
        
        return min(similarity, 1.0)
    
    def map_entity(self, extracted_entity: ExtractedEntity) -> EntityMapping:
        """映射实体"""
        # 1. 尝试精确匹配
        exact_match_entity = self.exact_match(extracted_entity)
        if exact_match_entity:
            return EntityMapping(
                extracted_entity=extracted_entity,
                mapped_entity=exact_match_entity,
                confidence=1.0,
                mapping_type='exact',
                similarity_score=1.0
            )
        
        # 2. 尝试模糊匹配
        fuzzy_candidates = self.fuzzy_match(extracted_entity)
        if fuzzy_candidates:
            best_candidate, similarity = fuzzy_candidates[0]
            return EntityMapping(
                extracted_entity=extracted_entity,
                mapped_entity=best_candidate,
                confidence=similarity,
                mapping_type='fuzzy',
                similarity_score=similarity
            )
        
        # 3. 尝试语义匹配
        semantic_candidates = self.semantic_match(extracted_entity)
        if semantic_candidates:
            best_candidate, similarity = semantic_candidates[0]
            return EntityMapping(
                extracted_entity=extracted_entity,
                mapped_entity=best_candidate,
                confidence=similarity,
                mapping_type='semantic',
                similarity_score=similarity
            )
        
        # 4. 创建新实体
        return EntityMapping(
            extracted_entity=extracted_entity,
            mapped_entity=None,
            confidence=0.0,
            mapping_type='new',
            similarity_score=0.0
        )
    
    def batch_map_entities(self, extracted_entities: List[ExtractedEntity]) -> List[EntityMapping]:
        """批量映射实体"""
        mappings = []
        
        for extracted_entity in extracted_entities:
            mapping = self.map_entity(extracted_entity)
            mappings.append(mapping)
        
        return mappings
    
    def create_new_entity(self, extracted_entity: ExtractedEntity, entity_id: str = None) -> Entity:
        """基于抽取的实体创建新的标准实体"""
        if not entity_id:
            entity_id = f"entity_{len(self.known_entities)}"
        
        properties = {}
        if hasattr(extracted_entity, 'confidence'):
            properties['extraction_confidence'] = extracted_entity.confidence
        if hasattr(extracted_entity, 'context'):
            properties['context'] = extracted_entity.context
        
        new_entity = Entity(
            id=entity_id,
            name=extracted_entity.text,
            type=extracted_entity.type,
            properties=properties
        )
        
        # 添加到已知实体库
        self.add_known_entity(new_entity)
        
        return new_entity
    
    def suggest_aliases(self, entity: Entity, extracted_entities: List[ExtractedEntity]) -> List[str]:
        """为实体建议别名"""
        suggestions = []
        
        for extracted_entity in extracted_entities:
            if (extracted_entity.type == entity.type and 
                extracted_entity.text != entity.name):
                
                # 计算相似度
                similarity = self._calculate_string_similarity(
                    self.normalize_entity_name(entity.name),
                    self.normalize_entity_name(extracted_entity.text)
                )
                
                if 0.7 <= similarity < 0.9:  # 足够相似但不完全相同
                    suggestions.append(extracted_entity.text)
        
        return list(set(suggestions))  # 去重
    
    def get_mapping_statistics(self, mappings: List[EntityMapping]) -> Dict[str, int]:
        """获取映射统计信息"""
        stats = {
            'total': len(mappings),
            'exact': 0,
            'fuzzy': 0,
            'semantic': 0,
            'new': 0,
            'high_confidence': 0,  # > 0.8
            'medium_confidence': 0,  # 0.5 - 0.8
            'low_confidence': 0  # < 0.5
        }
        
        for mapping in mappings:
            stats[mapping.mapping_type] += 1
            
            if mapping.confidence > 0.8:
                stats['high_confidence'] += 1
            elif mapping.confidence > 0.5:
                stats['medium_confidence'] += 1
            else:
                stats['low_confidence'] += 1
        
        return stats
    
    def print_mapping_results(self, mappings: List[EntityMapping]):
        """打印映射结果"""
        stats = self.get_mapping_statistics(mappings)
        
        print(f"实体映射结果 ({stats['total']} 个实体):")
        print(f"  精确匹配: {stats['exact']}")
        print(f"  模糊匹配: {stats['fuzzy']}")
        print(f"  语义匹配: {stats['semantic']}")
        print(f"  新实体: {stats['new']}")
        
        print(f"\n置信度分布:")
        print(f"  高置信度 (>0.8): {stats['high_confidence']}")
        print(f"  中等置信度 (0.5-0.8): {stats['medium_confidence']}")
        print(f"  低置信度 (<0.5): {stats['low_confidence']}")
        
        # 显示一些具体的映射示例
        print(f"\n映射示例:")
        for i, mapping in enumerate(mappings[:5]):
            mapped_name = mapping.mapped_entity.name if mapping.mapped_entity else "新实体"
            print(f"  {mapping.extracted_entity.text} -> {mapped_name} "
                  f"({mapping.mapping_type}, 置信度: {mapping.confidence:.2f})")