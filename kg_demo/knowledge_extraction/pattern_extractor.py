"""
模式抽取模块 - 发现和学习新的抽取模式
"""
import re
from typing import List, Dict, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
from .entity_extractor import ExtractedEntity
from .relation_extractor import ExtractedRelation


@dataclass
class Pattern:
    """抽取模式"""
    pattern_text: str
    pattern_type: str  # 'entity' or 'relation'
    target_type: str   # 实体类型或关系类型
    confidence: float
    frequency: int
    examples: List[str]


class PatternExtractor:
    """模式抽取器"""
    
    def __init__(self):
        self.entity_patterns = defaultdict(list)
        self.relation_patterns = defaultdict(list)
        self.learned_patterns = []
    
    def discover_entity_patterns(self, texts: List[str], 
                                entities: List[List[ExtractedEntity]]) -> List[Pattern]:
        """发现实体抽取模式"""
        patterns = []
        entity_contexts = defaultdict(list)
        
        # 收集实体上下文
        for text, text_entities in zip(texts, entities):
            for entity in text_entities:
                context = self._get_entity_context(text, entity)
                entity_contexts[entity.type].append({
                    'entity': entity.text,
                    'context': context,
                    'before': context['before'],
                    'after': context['after']
                })
        
        # 分析每种实体类型的模式
        for entity_type, contexts in entity_contexts.items():
            # 前缀模式
            before_patterns = self._extract_prefix_patterns(contexts)
            for pattern_text, freq in before_patterns.items():
                if freq >= 2:  # 至少出现2次
                    confidence = min(1.0, freq / len(contexts))
                    examples = [ctx['entity'] for ctx in contexts 
                              if pattern_text in ctx['before']][:5]
                    
                    pattern = Pattern(
                        pattern_text=pattern_text,
                        pattern_type='entity',
                        target_type=entity_type,
                        confidence=confidence,
                        frequency=freq,
                        examples=examples
                    )
                    patterns.append(pattern)
            
            # 后缀模式
            after_patterns = self._extract_suffix_patterns(contexts)
            for pattern_text, freq in after_patterns.items():
                if freq >= 2:
                    confidence = min(1.0, freq / len(contexts))
                    examples = [ctx['entity'] for ctx in contexts 
                              if pattern_text in ctx['after']][:5]
                    
                    pattern = Pattern(
                        pattern_text=pattern_text,
                        pattern_type='entity',
                        target_type=entity_type,
                        confidence=confidence,
                        frequency=freq,
                        examples=examples
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def discover_relation_patterns(self, texts: List[str], 
                                 relations: List[List[ExtractedRelation]]) -> List[Pattern]:
        """发现关系抽取模式"""
        patterns = []
        relation_contexts = defaultdict(list)
        
        # 收集关系上下文
        for text, text_relations in zip(texts, relations):
            for relation in text_relations:
                context = self._get_relation_context(text, relation)
                relation_contexts[relation.relation_type].append({
                    'head': relation.head_entity,
                    'tail': relation.tail_entity,
                    'context': context,
                    'middle': context['middle']
                })
        
        # 分析每种关系类型的模式
        for relation_type, contexts in relation_contexts.items():
            middle_patterns = self._extract_middle_patterns(contexts)
            
            for pattern_text, freq in middle_patterns.items():
                if freq >= 2:
                    confidence = min(1.0, freq / len(contexts))
                    examples = [f"{ctx['head']} -> {ctx['tail']}" for ctx in contexts 
                              if pattern_text in ctx['middle']][:5]
                    
                    pattern = Pattern(
                        pattern_text=pattern_text,
                        pattern_type='relation',
                        target_type=relation_type,
                        confidence=confidence,
                        frequency=freq,
                        examples=examples
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _get_entity_context(self, text: str, entity: ExtractedEntity, 
                           window_size: int = 10) -> Dict[str, str]:
        """获取实体的上下文信息"""
        start, end = entity.start_pos, entity.end_pos
        
        before_start = max(0, start - window_size)
        after_end = min(len(text), end + window_size)
        
        return {
            'before': text[before_start:start],
            'entity': text[start:end],
            'after': text[end:after_end],
            'full': text[before_start:after_end]
        }
    
    def _get_relation_context(self, text: str, relation: ExtractedRelation,
                             window_size: int = 5) -> Dict[str, str]:
        """获取关系的上下文信息"""
        # 简化处理：假设头尾实体在文本中的位置
        head_pos = text.find(relation.head_entity)
        tail_pos = text.find(relation.tail_entity, head_pos + len(relation.head_entity))
        
        if head_pos == -1 or tail_pos == -1:
            return {'middle': '', 'before': '', 'after': ''}
        
        head_end = head_pos + len(relation.head_entity)
        
        before_start = max(0, head_pos - window_size)
        after_end = min(len(text), tail_pos + len(relation.tail_entity) + window_size)
        
        return {
            'before': text[before_start:head_pos],
            'head': text[head_pos:head_end],
            'middle': text[head_end:tail_pos],
            'tail': text[tail_pos:tail_pos + len(relation.tail_entity)],
            'after': text[tail_pos + len(relation.tail_entity):after_end],
            'full': text[before_start:after_end]
        }
    
    def _extract_prefix_patterns(self, contexts: List[Dict]) -> Counter:
        """提取前缀模式"""
        patterns = Counter()
        
        for context in contexts:
            before_text = context['before'].strip()
            if not before_text:
                continue
            
            # 提取词汇模式
            words = before_text.split()
            if words:
                # 最后一个词
                patterns[words[-1]] += 1
                
                # 最后两个词
                if len(words) >= 2:
                    patterns[' '.join(words[-2:])] += 1
            
            # 提取字符模式
            if len(before_text) >= 1:
                patterns[before_text[-1:]] += 1
            if len(before_text) >= 2:
                patterns[before_text[-2:]] += 1
        
        return patterns
    
    def _extract_suffix_patterns(self, contexts: List[Dict]) -> Counter:
        """提取后缀模式"""
        patterns = Counter()
        
        for context in contexts:
            after_text = context['after'].strip()
            if not after_text:
                continue
            
            # 提取词汇模式
            words = after_text.split()
            if words:
                # 第一个词
                patterns[words[0]] += 1
                
                # 前两个词
                if len(words) >= 2:
                    patterns[' '.join(words[:2])] += 1
            
            # 提取字符模式
            if len(after_text) >= 1:
                patterns[after_text[:1]] += 1
            if len(after_text) >= 2:
                patterns[after_text[:2]] += 1
        
        return patterns
    
    def _extract_middle_patterns(self, contexts: List[Dict]) -> Counter:
        """提取中间模式（用于关系）"""
        patterns = Counter()
        
        for context in contexts:
            middle_text = context['middle'].strip()
            if not middle_text:
                continue
            
            # 清理文本
            cleaned = re.sub(r'\s+', ' ', middle_text)
            
            # 整个中间文本
            patterns[cleaned] += 1
            
            # 提取关键词
            words = cleaned.split()
            for word in words:
                if len(word) > 1 and not word.isdigit():
                    patterns[word] += 1
        
        return patterns
    
    def learn_patterns_from_seeds(self, texts: List[str], 
                                 seed_entities: Dict[str, List[str]],
                                 seed_relations: Dict[str, List[Tuple[str, str]]]) -> List[Pattern]:
        """从种子实体和关系学习模式"""
        learned_patterns = []
        
        # 从种子实体学习
        for entity_type, entity_list in seed_entities.items():
            contexts = []
            
            for text in texts:
                for entity in entity_list:
                    positions = self._find_all_positions(text, entity)
                    for pos in positions:
                        context = {
                            'entity': entity,
                            'before': text[max(0, pos-10):pos],
                            'after': text[pos+len(entity):pos+len(entity)+10]
                        }
                        contexts.append(context)
            
            if contexts:
                # 提取模式
                before_patterns = self._extract_prefix_patterns(contexts)
                after_patterns = self._extract_suffix_patterns(contexts)
                
                # 转换为Pattern对象
                for pattern_text, freq in before_patterns.items():
                    if freq >= 2:
                        pattern = Pattern(
                            pattern_text=pattern_text,
                            pattern_type='entity',
                            target_type=entity_type,
                            confidence=freq / len(contexts),
                            frequency=freq,
                            examples=[ctx['entity'] for ctx in contexts 
                                    if pattern_text in ctx['before']][:3]
                        )
                        learned_patterns.append(pattern)
        
        return learned_patterns
    
    def _find_all_positions(self, text: str, substring: str) -> List[int]:
        """找到子字符串在文本中的所有位置"""
        positions = []
        start = 0
        while True:
            pos = text.find(substring, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        return positions
    
    def validate_patterns(self, patterns: List[Pattern], 
                         validation_texts: List[str]) -> List[Pattern]:
        """验证模式的有效性"""
        validated_patterns = []
        
        for pattern in patterns:
            # 在验证集上测试模式
            matches = 0
            total_attempts = 0
            
            for text in validation_texts:
                if pattern.pattern_type == 'entity':
                    # 测试实体模式
                    pattern_matches = self._test_entity_pattern(text, pattern)
                    matches += len(pattern_matches)
                    total_attempts += 1
                
                elif pattern.pattern_type == 'relation':
                    # 测试关系模式
                    pattern_matches = self._test_relation_pattern(text, pattern)
                    matches += len(pattern_matches)
                    total_attempts += 1
            
            # 计算验证置信度
            if total_attempts > 0:
                validation_confidence = matches / total_attempts
                if validation_confidence > 0.1:  # 阈值
                    pattern.confidence = (pattern.confidence + validation_confidence) / 2
                    validated_patterns.append(pattern)
        
        return validated_patterns
    
    def _test_entity_pattern(self, text: str, pattern: Pattern) -> List[str]:
        """测试实体模式"""
        matches = []
        # 简化的模式测试
        if pattern.pattern_text in text:
            # 查找模式后的潜在实体
            positions = self._find_all_positions(text, pattern.pattern_text)
            for pos in positions:
                start = pos + len(pattern.pattern_text)
                # 提取后续的词作为潜在实体
                remaining = text[start:start+20]
                words = remaining.split()
                if words:
                    matches.append(words[0])
        
        return matches
    
    def _test_relation_pattern(self, text: str, pattern: Pattern) -> List[Tuple[str, str]]:
        """测试关系模式"""
        matches = []
        # 简化的关系模式测试
        # 实际应用中需要更复杂的逻辑
        return matches
    
    def export_patterns(self, patterns: List[Pattern], filepath: str):
        """导出学习到的模式"""
        import json
        
        pattern_data = []
        for pattern in patterns:
            pattern_data.append({
                'pattern_text': pattern.pattern_text,
                'pattern_type': pattern.pattern_type,
                'target_type': pattern.target_type,
                'confidence': pattern.confidence,
                'frequency': pattern.frequency,
                'examples': pattern.examples
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pattern_data, f, ensure_ascii=False, indent=2)
    
    def load_patterns(self, filepath: str) -> List[Pattern]:
        """加载模式"""
        import json
        
        with open(filepath, 'r', encoding='utf-8') as f:
            pattern_data = json.load(f)
        
        patterns = []
        for data in pattern_data:
            pattern = Pattern(
                pattern_text=data['pattern_text'],
                pattern_type=data['pattern_type'],
                target_type=data['target_type'],
                confidence=data['confidence'],
                frequency=data['frequency'],
                examples=data['examples']
            )
            patterns.append(pattern)
        
        return patterns
    
    def print_patterns(self, patterns: List[Pattern]):
        """打印模式信息"""
        print(f"发现 {len(patterns)} 个模式:")
        
        # 按类型分组
        entity_patterns = [p for p in patterns if p.pattern_type == 'entity']
        relation_patterns = [p for p in patterns if p.pattern_type == 'relation']
        
        if entity_patterns:
            print(f"\n实体模式 ({len(entity_patterns)}):")
            for pattern in entity_patterns:
                print(f"  - [{pattern.target_type}] '{pattern.pattern_text}' "
                      f"(置信度: {pattern.confidence:.2f}, 频次: {pattern.frequency})")
                print(f"    示例: {', '.join(pattern.examples[:3])}")
        
        if relation_patterns:
            print(f"\n关系模式 ({len(relation_patterns)}):")
            for pattern in relation_patterns:
                print(f"  - [{pattern.target_type}] '{pattern.pattern_text}' "
                      f"(置信度: {pattern.confidence:.2f}, 频次: {pattern.frequency})")
                print(f"    示例: {', '.join(pattern.examples[:3])}")