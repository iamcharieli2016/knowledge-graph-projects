"""
文本预处理和特征提取模块
"""
import re
import jieba
import jieba.posseg as pseg
from typing import List, Dict, Tuple
import pandas as pd


class TextExtractor:
    """文本提取和预处理类"""
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
        # 添加自定义词典
        jieba.load_userdict(self._create_custom_dict())
    
    def _load_stop_words(self) -> set:
        """加载停用词"""
        # 基本停用词集合
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这', '那', '里', '来', '关于', '对于', '由于'
        }
        return stop_words
    
    def _create_custom_dict(self) -> str:
        """创建自定义词典"""
        import os
        from pathlib import Path
        
        custom_words = [
            "知识图谱", "人工智能", "机器学习", "深度学习", "自然语言处理",
            "实体识别", "关系抽取", "本体构建", "语义网", "图数据库"
        ]
        
        # 获取绝对路径
        current_dir = Path(__file__).parent.parent
        dict_file = current_dir / 'data' / 'custom_dict.txt'
        
        # 确保目录存在
        dict_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(dict_file, 'w', encoding='utf-8') as f:
            for word in custom_words:
                f.write(f"{word}\n")
        
        return str(dict_file)
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 清理HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 清理特殊字符，保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,;!?()（），。；！？]', '', text)
        
        # 规范化空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """中文分词"""
        text = self.preprocess_text(text)
        tokens = jieba.lcut(text)
        
        # 过滤停用词和短词
        filtered_tokens = [
            token for token in tokens 
            if token not in self.stop_words and len(token.strip()) > 1
        ]
        
        return filtered_tokens
    
    def pos_tagging(self, text: str) -> List[Tuple[str, str]]:
        """词性标注"""
        text = self.preprocess_text(text)
        words_with_pos = pseg.lcut(text)
        
        return [(word, pos) for word, pos in words_with_pos if word not in self.stop_words]
    
    def extract_sentences(self, text: str) -> List[str]:
        """句子分割"""
        # 按标点符号分割句子
        sentences = re.split(r'[。！？；\n]', text)
        
        # 清理空句子和过短的句子
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        return sentences
    
    def extract_noun_phrases(self, text: str) -> List[str]:
        """提取名词短语"""
        words_with_pos = self.pos_tagging(text)
        noun_phrases = []
        
        current_phrase = []
        for word, pos in words_with_pos:
            # 名词相关词性: n(名词), nr(人名), ns(地名), nt(机构名), nz(其他专名)
            if pos.startswith('n') or pos in ['a', 'v']:  # 包括形容词和动词作修饰
                current_phrase.append(word)
            else:
                if len(current_phrase) >= 2:
                    noun_phrases.append(''.join(current_phrase))
                current_phrase = []
        
        # 处理最后一个短语
        if len(current_phrase) >= 2:
            noun_phrases.append(''.join(current_phrase))
        
        return list(set(noun_phrases))  # 去重
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词（基于TF-IDF的简化版本）"""
        words = self.tokenize(text)
        
        # 计算词频
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按词频排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:top_k]]
    
    def extract_patterns(self, text: str) -> Dict[str, List[str]]:
        """提取常见的实体和关系模式"""
        patterns = {
            'person_org': [],  # 人物-组织关系
            'location': [],    # 地点信息
            'time': [],        # 时间信息
            'numbers': []      # 数字信息
        }
        
        # 人物-组织关系模式
        person_org_pattern = re.findall(r'(\w+)(?:在|就职于|工作于|任职于)(\w+)', text)
        patterns['person_org'] = [(p, o) for p, o in person_org_pattern]
        
        # 地点模式
        location_pattern = re.findall(r'(\w+)(?:位于|在|坐落于)(\w+)', text)
        patterns['location'] = [(l1, l2) for l1, l2 in location_pattern]
        
        # 时间模式
        time_pattern = re.findall(r'(\d{4})年|(\d{1,2})月|(\d{1,2})日', text)
        patterns['time'] = [t for t in time_pattern if any(t)]
        
        # 数字模式  
        number_pattern = re.findall(r'\d+(?:\.\d+)?(?:万|亿|千|百)?', text)
        patterns['numbers'] = number_pattern
        
        return patterns
    
    def batch_process(self, texts: List[str]) -> pd.DataFrame:
        """批量处理文本"""
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = {
                    'id': i,
                    'original_text': text,
                    'processed_text': self.preprocess_text(text),
                    'tokens': self.tokenize(text),
                    'sentences': self.extract_sentences(text),
                    'noun_phrases': self.extract_noun_phrases(text),
                    'keywords': self.extract_keywords(text),
                    'patterns': self.extract_patterns(text)
                }
                results.append(result)
            except Exception as e:
                print(f"处理文本 {i} 时出错: {e}")
                continue
        
        return pd.DataFrame(results)