"""
关系抽取模块
"""
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .entity_extractor import ExtractedEntity
from ..entity_definition.relation_types import Relation


@dataclass
class ExtractedRelation:
    """抽取的关系"""
    head_entity: str
    relation_type: str
    tail_entity: str
    confidence: float
    context: str
    start_pos: int = 0
    end_pos: int = 0


class RelationExtractor:
    """关系抽取器"""
    
    def __init__(self):
        self.relation_patterns = self._build_relation_patterns()
        self.dependency_patterns = self._build_dependency_patterns()
    
    def _build_relation_patterns(self) -> Dict[str, List[Dict]]:
        """构建关系抽取模式"""
        patterns = {
            'works_for': [
                # 基础模式，将在extract_by_patterns中动态替换实体
                {'pattern': r'({person})(?:是)({organization})(?:的)(?:教授|研究员|老师|学者)', 'confidence': 0.95},
                {'pattern': r'({person})(?:在)({organization})(?:工作|任职|就职)', 'confidence': 0.9},
                {'pattern': r'({person})(?:担任|任)({organization})(?:的|)(?:职位|工作|CEO|CTO)', 'confidence': 0.85}
            ],
            'located_in': [
                {'pattern': r'(\w+)(?:位于|坐落于|在)(\w+)', 'confidence': 0.9},
                {'pattern': r'(\w+)(?:的|)总部(?:在|位于)(\w+)', 'confidence': 0.8},
                {'pattern': r'(\w+)(?:设立|建立)(?:在|于)(\w+)', 'confidence': 0.7}
            ],
            'born_in': [
                {'pattern': r'(\w+)(?:出生于|生于)(\w+)', 'confidence': 0.9},
                {'pattern': r'(\w+)(?:是|)(\w+)人', 'confidence': 0.6}
            ],
            'graduated_from': [
                {'pattern': r'({person})(?:毕业于|毕业|就读于|就读)({organization})', 'confidence': 0.95},
                {'pattern': r'({person})(?:在)({organization})(?:学习|读书)', 'confidence': 0.85},
                {'pattern': r'({person})(?:是)({organization})(?:的|)(?:学生|毕业生)', 'confidence': 0.8}
            ],
            'founder_of': [
                {'pattern': r'({person})(?:创建|创立|创办|成立)(?:了|)({organization})', 'confidence': 0.95},
                {'pattern': r'({person})(?:在)(\d{4})(?:年)(?:创立|创建)(?:了|)({organization})', 'confidence': 0.9}
            ],
            'parent_of': [
                {'pattern': r'(\w+)(?:的|)(?:父亲|母亲|爸爸|妈妈)(?:是|)(\w+)', 'confidence': 0.9},
                {'pattern': r'(\w+)(?:和|与)(\w+)(?:是|)(?:父子|母子|父女|母女)关系', 'confidence': 0.8}
            ],
            'spouse_of': [
                {'pattern': r'(\w+)(?:和|与)(\w+)(?:结婚|夫妻|夫妇)', 'confidence': 0.9},
                {'pattern': r'(\w+)(?:的|)(?:丈夫|妻子|老公|老婆)(?:是|)(\w+)', 'confidence': 0.8}
            ],
            'participated_in': [
                {'pattern': r'(\w+)(?:参加|参与|出席)(?:了|)(\w+)', 'confidence': 0.8},
                {'pattern': r'(\w+)(?:在|于)(\w+)(?:中|上)(?:发言|演讲|表演)', 'confidence': 0.7}
            ],
            'produces': [
                {'pattern': r'(\w+)(?:生产|制造|开发)(?:了|)(\w+)', 'confidence': 0.8},
                {'pattern': r'(\w+)(?:推出|发布)(?:了|)(\w+)', 'confidence': 0.7}
            ],
            'occurred_at': [
                {'pattern': r'(\w+)(?:在|于)(\w+)(?:举行|进行|发生)', 'confidence': 0.8},
                {'pattern': r'(\w+)(?:的|)(?:地点|场所)(?:是|在)(\w+)', 'confidence': 0.7}
            ]
        }
        return patterns
    
    def _build_dependency_patterns(self) -> List[Dict]:
        """构建基于依存关系的模式"""
        # 简化的依存关系模式，实际应用中可以使用更复杂的NLP工具
        patterns = [
            {
                'head_pos': ['nr', 'n'],  # 人名或名词
                'relation_words': ['是', '担任', '任职'],
                'tail_pos': ['n', 'nt'],  # 名词或机构名
                'relation_type': 'works_for',
                'confidence': 0.7
            },
            {
                'head_pos': ['nt', 'ns'],  # 机构名或地名
                'relation_words': ['位于', '在', '坐落于'],
                'tail_pos': ['ns'],  # 地名
                'relation_type': 'located_in',
                'confidence': 0.8
            }
        ]
        return patterns
    
    def extract_by_patterns(self, text: str, entities: List[ExtractedEntity] = None) -> List[ExtractedRelation]:
        """基于模式的关系抽取 - 基于已抽取实体的精确匹配"""
        relations = []
        
        if not entities:
            return relations
        
        # 按类型分组实体
        person_entities = [e for e in entities if e.type == 'Person']
        org_entities = [e for e in entities if e.type == 'Organization']
        location_entities = [e for e in entities if e.type == 'Location']
        
        # 构建实体名称映射
        person_names = [e.text for e in person_entities]
        org_names = [e.text for e in org_entities]
        location_names = [e.text for e in location_entities]
        
        # works_for 关系
        for person in person_names:
            for org in org_names:
                # 检查各种工作关系模式
                patterns = [
                    f'{person}是{org}的教授',
                    f'{person}是{org}的研究员',
                    f'{person}是{org}的老师',
                    f'{person}在{org}工作',
                    f'{person}在{org}任职',
                ]
                
                for pattern in patterns:
                    if pattern in text:
                        relations.append(ExtractedRelation(
                            head_entity=person,
                            relation_type='works_for',
                            tail_entity=org,
                            confidence=0.9,
                            context=pattern,
                            start_pos=text.find(pattern),
                            end_pos=text.find(pattern) + len(pattern)
                        ))
                        break  # 找到一个就够了
        
        # graduated_from 关系
        for person in person_names:
            for org in org_names:
                patterns = [
                    f'{person}毕业于{org}',
                    f'{person}就读于{org}',
                ]
                
                for pattern in patterns:
                    if pattern in text:
                        relations.append(ExtractedRelation(
                            head_entity=person,
                            relation_type='graduated_from',
                            tail_entity=org,
                            confidence=0.95,
                            context=pattern,
                            start_pos=text.find(pattern),
                            end_pos=text.find(pattern) + len(pattern)
                        ))
                        break
        
        # founder_of 关系
        for person in person_names:
            for org in org_names:
                patterns = [
                    f'{person}创立了{org}',
                    f'{person}创建了{org}',
                    f'{person}创办了{org}',
                    f'{person}在2010年创立了{org}',  # 包含时间的模式
                ]
                
                for pattern in patterns:
                    if pattern in text or pattern.replace('了', '') in text:
                        relations.append(ExtractedRelation(
                            head_entity=person,
                            relation_type='founder_of',
                            tail_entity=org,
                            confidence=0.95,
                            context=pattern,
                            start_pos=text.find(pattern.replace('了', '')) if pattern.replace('了', '') in text else text.find(pattern),
                            end_pos=text.find(pattern.replace('了', '')) + len(pattern.replace('了', '')) if pattern.replace('了', '') in text else text.find(pattern) + len(pattern)
                        ))
                        break
        
        return relations
    
    def extract_by_distance(self, text: str, entities: List[ExtractedEntity], 
                          max_distance: int = 50) -> List[ExtractedRelation]:
        """基于实体距离的关系抽取"""
        relations = []
        
        # 按位置排序实体
        entities.sort(key=lambda x: x.start_pos)
        
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # 计算实体间距离
                distance = entity2.start_pos - entity1.end_pos
                if distance > max_distance:
                    break
                
                # 获取实体间文本
                between_text = text[entity1.end_pos:entity2.start_pos]
                
                # 查找可能的关系词
                relation_type = self._find_relation_in_text(between_text, entity1.type, entity2.type)
                
                if relation_type:
                    confidence = max(0.3, 1.0 - distance / max_distance)  # 距离越近置信度越高
                    
                    relation = ExtractedRelation(
                        head_entity=entity1.text,
                        relation_type=relation_type,
                        tail_entity=entity2.text,
                        confidence=confidence,
                        context=text[entity1.start_pos:entity2.end_pos],
                        start_pos=entity1.start_pos,
                        end_pos=entity2.end_pos
                    )
                    relations.append(relation)
        
        return relations
    
    def extract_by_templates(self, text: str, templates: List[Dict]) -> List[ExtractedRelation]:
        """基于模板的关系抽取"""
        relations = []
        
        for template in templates:
            pattern = template['pattern']
            relation_type = template['relation_type']
            confidence = template.get('confidence', 0.7)
            
            matches = re.finditer(pattern, text)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    head_entity = groups[0].strip()
                    tail_entity = groups[1].strip()
                    
                    relation = ExtractedRelation(
                        head_entity=head_entity,
                        relation_type=relation_type,
                        tail_entity=tail_entity,
                        confidence=confidence,
                        context=self._get_context(text, match.start(), match.end()),
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    relations.append(relation)
        
        return relations
    
    def _is_valid_entity_pair(self, head_entity: str, tail_entity: str, 
                             entities: List[ExtractedEntity] = None) -> bool:
        """验证实体对是否有效"""
        # 基本验证
        if not head_entity or not tail_entity:
            return False
        
        if head_entity == tail_entity:
            return False
        
        # 长度验证
        if len(head_entity) < 2 or len(tail_entity) < 2:
            return False
        
        # 如果提供了实体列表，检查实体是否存在
        if entities:
            entity_names = {entity.text for entity in entities}
            if head_entity not in entity_names or tail_entity not in entity_names:
                return False
        
        return True
    
    def _find_relation_in_text(self, text: str, head_type: str, tail_type: str) -> Optional[str]:
        """在文本中查找关系类型"""
        text = text.strip()
        
        # 工作关系指示词
        work_indicators = ['在', '就职于', '工作于', '任职于', '是', '担任']
        if any(indicator in text for indicator in work_indicators):
            if head_type == 'Person' and tail_type == 'Organization':
                return 'works_for'
        
        # 位置关系指示词
        location_indicators = ['位于', '在', '坐落于', '设在']
        if any(indicator in text for indicator in location_indicators):
            if tail_type == 'Location':
                return 'located_in'
        
        # 创建关系指示词
        founder_indicators = ['创建', '创立', '创办', '成立', '建立']
        if any(indicator in text for indicator in founder_indicators):
            if head_type == 'Person' and tail_type == 'Organization':
                return 'founder_of'
        
        # 参与关系指示词
        participate_indicators = ['参加', '参与', '出席']
        if any(indicator in text for indicator in participate_indicators):
            if head_type == 'Person' and tail_type == 'Event':
                return 'participated_in'
        
        return None
    
    def _get_context(self, text: str, start_pos: int, end_pos: int, window_size: int = 30) -> str:
        """获取关系的上下文"""
        context_start = max(0, start_pos - window_size)
        context_end = min(len(text), end_pos + window_size)
        return text[context_start:context_end]
    
    def merge_relations(self, relations: List[ExtractedRelation]) -> List[ExtractedRelation]:
        """合并重复的关系"""
        if not relations:
            return []
        
        # 按(头实体, 关系类型, 尾实体)分组
        relation_groups = {}
        
        for relation in relations:
            key = (relation.head_entity, relation.relation_type, relation.tail_entity)
            if key not in relation_groups:
                relation_groups[key] = []
            relation_groups[key].append(relation)
        
        # 对每组选择置信度最高的关系
        merged_relations = []
        for group in relation_groups.values():
            best_relation = max(group, key=lambda x: x.confidence)
            merged_relations.append(best_relation)
        
        return merged_relations
    
    def filter_relations(self, relations: List[ExtractedRelation], 
                        min_confidence: float = 0.3) -> List[ExtractedRelation]:
        """过滤关系"""
        return [rel for rel in relations if rel.confidence >= min_confidence]
    
    def extract_relations(self, text: str, 
                         entities: List[ExtractedEntity] = None,
                         templates: List[Dict] = None,
                         use_patterns: bool = True,
                         use_distance: bool = False,  # 默认禁用距离抽取
                         use_templates: bool = False) -> List[ExtractedRelation]:
        """综合关系抽取"""
        all_relations = []
        
        # 基于模式的抽取
        if use_patterns:
            pattern_relations = self.extract_by_patterns(text, entities)
            all_relations.extend(pattern_relations)
        
        # 基于距离的抽取 (默认禁用)
        if use_distance and entities:
            distance_relations = self.extract_by_distance(text, entities)
            all_relations.extend(distance_relations)
        
        # 基于模板的抽取
        if use_templates and templates:
            template_relations = self.extract_by_templates(text, templates)
            all_relations.extend(template_relations)
        
        # 合并和过滤
        merged_relations = self.merge_relations(all_relations)
        filtered_relations = self.filter_relations(merged_relations)
        
        return filtered_relations
    
    def relations_to_kg_format(self, relations: List[ExtractedRelation], 
                              entity_mapping: Dict[str, str] = None) -> List[Relation]:
        """将抽取的关系转换为知识图谱格式"""
        kg_relations = []
        
        for i, extracted_relation in enumerate(relations):
            # 获取实体ID
            head_entity_id = entity_mapping.get(extracted_relation.head_entity, 
                                               f"entity_{extracted_relation.head_entity}")
            tail_entity_id = entity_mapping.get(extracted_relation.tail_entity,
                                               f"entity_{extracted_relation.tail_entity}")
            
            relation = Relation(
                id=f"relation_{i}",
                type=extracted_relation.relation_type,
                head_entity_id=head_entity_id,
                tail_entity_id=tail_entity_id,
                properties={
                    "context": extracted_relation.context,
                    "source_position": f"{extracted_relation.start_pos}-{extracted_relation.end_pos}"
                },
                confidence=extracted_relation.confidence
            )
            kg_relations.append(relation)
        
        return kg_relations
    
    def print_extraction_results(self, relations: List[ExtractedRelation]):
        """打印关系抽取结果"""
        print(f"抽取到 {len(relations)} 个关系:")
        
        # 按关系类型分组
        by_type = {}
        for relation in relations:
            if relation.relation_type not in by_type:
                by_type[relation.relation_type] = []
            by_type[relation.relation_type].append(relation)
        
        for relation_type, type_relations in by_type.items():
            print(f"\n{relation_type} ({len(type_relations)}):")
            for relation in type_relations:
                print(f"  - {relation.head_entity} -> {relation.tail_entity} "
                      f"(置信度: {relation.confidence:.2f})")