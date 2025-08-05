"""
实体抽取模块
"""
import re
import jieba.posseg as pseg
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from ..entity_definition.entity_types import Entity


@dataclass
class ExtractedEntity:
    """抽取的实体"""
    text: str
    type: str
    start_pos: int
    end_pos: int
    confidence: float
    context: str = ""


class EntityExtractor:
    """实体抽取器"""
    
    def __init__(self):
        self.entity_patterns = self._build_entity_patterns()
        self.person_indicators = {'先生', '女士', '教授', '博士', '院士', '总裁', '董事长', '经理'}
        self.org_indicators = {'公司', '企业', '集团', '组织', '机构', '学院', '大学', '医院'}
        self.location_indicators = {'市', '县', '区', '省', '国', '州', '路', '街', '镇', '村'}
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """构建实体识别模式"""
        patterns = {
            'Person': [
                r'[a-zA-Z][a-zA-Z\s]+',  # 英文姓名
                r'[\u4e00-\u9fa5]{2,4}(?:先生|女士|教授|博士|院士)',  # 带称谓的中文姓名
                r'[\u4e00-\u9fa5]{2,3}(?=说|表示|认为|指出)'  # 后接发言动词的姓名
            ],
            'Organization': [
                r'[\u4e00-\u9fa5]+(?:公司|集团|企业|机构|组织)',
                r'[\u4e00-\u9fa5]+(?:大学|学院|学校|医院)',
                r'[\u4e00-\u9fa5]+(?:政府|部门|委员会)'
            ],
            'Location': [
                r'[\u4e00-\u9fa5]+(?:市|县|区|省|国)',
                r'[\u4e00-\u9fa5]+(?:路|街|镇|村|社区)',
                r'[\u4e00-\u9fa5]+(?:山|河|湖|海)'
            ],
            'Product': [
                r'[\u4e00-\u9fa5a-zA-Z0-9]+(?:软件|系统|平台|应用)',
                r'iPhone\s*\d+|iPad|MacBook',
                r'Windows\s*\d+|Android'
            ],
            'Event': [
                r'[\u4e00-\u9fa5]+(?:会议|论坛|峰会|展览)',
                r'[\u4e00-\u9fa5]+(?:比赛|竞赛|锦标赛)',
                r'[\u4e00-\u9fa5]+(?:节|庆典|仪式)'
            ]
        }
        return patterns
    
    def extract_by_patterns(self, text: str) -> List[ExtractedEntity]:
        """基于模式的实体抽取"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity = ExtractedEntity(
                        text=match.group(),
                        type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.8,
                        context=self._get_context(text, match.start(), match.end())
                    )
                    entities.append(entity)
        
        return entities
    
    def extract_by_pos_tagging(self, text: str) -> List[ExtractedEntity]:
        """基于词性标注的实体抽取"""
        entities = []
        words_with_pos = pseg.lcut(text)
        
        current_pos = 0
        for word, pos in words_with_pos:
            entity_type = self._pos_to_entity_type(word, pos)
            if entity_type:
                start_pos = text.find(word, current_pos)
                end_pos = start_pos + len(word)
                
                entity = ExtractedEntity(
                    text=word,
                    type=entity_type,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    confidence=0.7,
                    context=self._get_context(text, start_pos, end_pos)
                )
                entities.append(entity)
            
            current_pos += len(word)
        
        return entities
    
    def _pos_to_entity_type(self, word: str, pos: str) -> str:
        """根据词性推断实体类型"""
        if pos == 'nr':  # 人名
            return 'Person'
        elif pos == 'ns':  # 地名
            return 'Location'
        elif pos == 'nt':  # 机构名
            return 'Organization'
        elif pos == 'n':  # 普通名词，需要进一步判断
            if any(indicator in word for indicator in self.person_indicators):
                return 'Person'
            elif any(indicator in word for indicator in self.org_indicators):
                return 'Organization'
            elif any(indicator in word for indicator in self.location_indicators):
                return 'Location'
        
        return None
    
    def extract_by_dictionary(self, text: str, entity_dict: Dict[str, str]) -> List[ExtractedEntity]:
        """基于字典的实体抽取"""
        entities = []
        
        for entity_name, entity_type in entity_dict.items():
            start = 0
            while True:
                pos = text.find(entity_name, start)
                if pos == -1:
                    break
                
                entity = ExtractedEntity(
                    text=entity_name,
                    type=entity_type,
                    start_pos=pos,
                    end_pos=pos + len(entity_name),
                    confidence=1.0,
                    context=self._get_context(text, pos, pos + len(entity_name))
                )
                entities.append(entity)
                start = pos + 1
        
        return entities
    
    def _get_context(self, text: str, start_pos: int, end_pos: int, window_size: int = 20) -> str:
        """获取实体的上下文"""
        context_start = max(0, start_pos - window_size)
        context_end = min(len(text), end_pos + window_size)
        return text[context_start:context_end]
    
    def merge_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """合并重叠的实体"""
        if not entities:
            return []
        
        # 按位置排序
        entities.sort(key=lambda x: (x.start_pos, x.end_pos))
        
        merged = [entities[0]]
        
        for current in entities[1:]:
            last = merged[-1]
            
            # 检查是否重叠
            if current.start_pos <= last.end_pos:
                # 选择置信度更高的实体
                if current.confidence > last.confidence:
                    merged[-1] = current
            else:
                merged.append(current)
        
        return merged
    
    def filter_entities(self, entities: List[ExtractedEntity], 
                       min_confidence: float = 0.5,
                       min_length: int = 2) -> List[ExtractedEntity]:
        """过滤实体"""
        filtered = []
        
        for entity in entities:
            # 过滤低置信度实体
            if entity.confidence < min_confidence:
                continue
            
            # 过滤过短的实体
            if len(entity.text) < min_length:
                continue
            
            # 过滤纯数字或纯符号
            if entity.text.isdigit() or not any(c.isalnum() for c in entity.text):
                continue
            
            filtered.append(entity)
        
        return filtered
    
    def extract_entities(self, text: str, 
                        entity_dict: Dict[str, str] = None,
                        use_patterns: bool = True,
                        use_pos: bool = True,
                        use_dict: bool = True) -> List[ExtractedEntity]:
        """综合实体抽取"""
        all_entities = []
        
        # 基于模式的抽取
        if use_patterns:
            pattern_entities = self.extract_by_patterns(text)
            all_entities.extend(pattern_entities)
        
        # 基于词性的抽取
        if use_pos:
            pos_entities = self.extract_by_pos_tagging(text)
            all_entities.extend(pos_entities)
        
        # 基于字典的抽取
        if use_dict and entity_dict:
            dict_entities = self.extract_by_dictionary(text, entity_dict)
            all_entities.extend(dict_entities)
        
        # 合并和过滤
        merged_entities = self.merge_entities(all_entities)
        filtered_entities = self.filter_entities(merged_entities)
        
        return filtered_entities
    
    def entities_to_kg_format(self, entities: List[ExtractedEntity]) -> List[Entity]:
        """将抽取的实体转换为知识图谱格式"""
        kg_entities = []
        
        for i, extracted_entity in enumerate(entities):
            entity = Entity(
                id=f"entity_{i}",
                name=extracted_entity.text,
                type=extracted_entity.type,
                properties={
                    "confidence": extracted_entity.confidence,
                    "context": extracted_entity.context,
                    "source_position": f"{extracted_entity.start_pos}-{extracted_entity.end_pos}"
                }
            )
            kg_entities.append(entity)
        
        return kg_entities
    
    def print_extraction_results(self, entities: List[ExtractedEntity]):
        """打印抽取结果"""
        print(f"抽取到 {len(entities)} 个实体:")
        
        # 按类型分组
        by_type = {}
        for entity in entities:
            if entity.type not in by_type:
                by_type[entity.type] = []
            by_type[entity.type].append(entity)
        
        for entity_type, type_entities in by_type.items():
            print(f"\n{entity_type} ({len(type_entities)}):")
            for entity in type_entities:
                print(f"  - {entity.text} (置信度: {entity.confidence:.2f})")