"""
相似度计算模块 - 提供各种相似度计算方法
"""
import re
import math
from typing import List, Dict, Tuple, Set, Any
from collections import Counter
from Levenshtein import distance as levenshtein_distance
import jieba


class SimilarityCalculator:
    """相似度计算器"""
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
    
    def _load_stop_words(self) -> Set[str]:
        """加载停用词"""
        return {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有'
        }
    
    def string_similarity(self, str1: str, str2: str, method: str = 'combined') -> float:
        """字符串相似度计算"""
        if not str1 or not str2:
            return 0.0
        
        if str1 == str2:
            return 1.0
        
        if method == 'levenshtein':
            return self._levenshtein_similarity(str1, str2)
        elif method == 'jaccard':
            return self._jaccard_similarity(str1, str2)
        elif method == 'cosine':
            return self._cosine_similarity(str1, str2)
        elif method == 'lcs':
            return self._lcs_similarity(str1, str2)
        elif method == 'combined':
            return self._combined_string_similarity(str1, str2)
        else:
            raise ValueError(f"未知的相似度计算方法: {method}")
    
    def _levenshtein_similarity(self, str1: str, str2: str) -> float:
        """Levenshtein距离相似度"""
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(str1, str2)
        return 1.0 - (distance / max_len)
    
    def _jaccard_similarity(self, str1: str, str2: str, n_gram: int = 2) -> float:
        """Jaccard相似度（基于n-gram）"""
        def get_ngrams(text: str, n: int) -> Set[str]:
            if len(text) < n:
                return {text}
            return {text[i:i+n] for i in range(len(text) - n + 1)}
        
        ngrams1 = get_ngrams(str1.lower(), n_gram)
        ngrams2 = get_ngrams(str2.lower(), n_gram)
        
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        
        return intersection / union if union > 0 else 0.0
    
    def _cosine_similarity(self, str1: str, str2: str) -> float:
        """余弦相似度（基于字符频率）"""
        def get_char_freq(text: str) -> Counter:
            return Counter(text.lower())
        
        freq1 = get_char_freq(str1)
        freq2 = get_char_freq(str2)
        
        # 计算向量的点积
        dot_product = sum(freq1[char] * freq2[char] for char in freq1 if char in freq2)
        
        # 计算向量的模长
        norm1 = math.sqrt(sum(freq * freq for freq in freq1.values()))
        norm2 = math.sqrt(sum(freq * freq for freq in freq2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _lcs_similarity(self, str1: str, str2: str) -> float:
        """最长公共子序列相似度"""
        def lcs_length(s1: str, s2: str) -> int:
            m, n = len(s1), len(s2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s1[i-1] == s2[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            
            return dp[m][n]
        
        lcs_len = lcs_length(str1, str2)
        max_len = max(len(str1), len(str2))
        
        return (2.0 * lcs_len) / (len(str1) + len(str2)) if (len(str1) + len(str2)) > 0 else 0.0
    
    def _combined_string_similarity(self, str1: str, str2: str) -> float:
        """综合字符串相似度"""
        lev_sim = self._levenshtein_similarity(str1, str2)
        jaccard_sim = self._jaccard_similarity(str1, str2)
        cosine_sim = self._cosine_similarity(str1, str2)
        lcs_sim = self._lcs_similarity(str1, str2)
        
        # 加权综合
        combined = (lev_sim * 0.3 + jaccard_sim * 0.3 + cosine_sim * 0.2 + lcs_sim * 0.2)
        return combined
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """语义相似度（基于词汇重叠）"""
        # 分词
        words1 = set(jieba.lcut(text1.lower())) - self.stop_words
        words2 = set(jieba.lcut(text2.lower())) - self.stop_words
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        # 计算词汇重叠相似度
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def context_similarity(self, context1: str, context2: str) -> float:
        """上下文相似度"""
        # 提取关键词
        def extract_keywords(text: str) -> Set[str]:
            words = jieba.lcut(text.lower())
            # 过滤停用词和短词
            keywords = {word for word in words 
                       if word not in self.stop_words and len(word) > 1}
            return keywords
        
        keywords1 = extract_keywords(context1)
        keywords2 = extract_keywords(context2)
        
        if not keywords1 and not keywords2:
            return 1.0
        if not keywords1 or not keywords2:
            return 0.0
        
        # 计算关键词重叠
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    
    def structural_similarity(self, structure1: Dict[str, Any], 
                            structure2: Dict[str, Any]) -> float:
        """结构相似度（比较字典结构）"""
        if not structure1 and not structure2:
            return 1.0
        if not structure1 or not structure2:
            return 0.0
        
        # 比较键的相似度
        keys1 = set(structure1.keys())
        keys2 = set(structure2.keys())
        
        key_intersection = len(keys1 & keys2)
        key_union = len(keys1 | keys2)
        key_similarity = key_intersection / key_union if key_union > 0 else 0.0
        
        # 比较值的相似度
        value_similarities = []
        common_keys = keys1 & keys2
        
        for key in common_keys:
            val1, val2 = structure1[key], structure2[key]
            
            if isinstance(val1, str) and isinstance(val2, str):
                val_sim = self.string_similarity(val1, val2)
            elif isinstance(val1, (list, set)) and isinstance(val2, (list, set)):
                val_sim = self._list_similarity(list(val1), list(val2))
            elif val1 == val2:
                val_sim = 1.0
            else:
                val_sim = 0.0
            
            value_similarities.append(val_sim)
        
        avg_value_similarity = sum(value_similarities) / len(value_similarities) \
                              if value_similarities else 0.0
        
        # 综合相似度
        return (key_similarity * 0.5 + avg_value_similarity * 0.5)
    
    def _list_similarity(self, list1: List[str], list2: List[str]) -> float:
        """列表相似度"""
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        set1 = set(list1)
        set2 = set(list2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def fuzzy_match_score(self, query: str, candidates: List[str], 
                         top_k: int = 5) -> List[Tuple[str, float]]:
        """模糊匹配评分"""
        scores = []
        
        for candidate in candidates:
            similarity = self.string_similarity(query, candidate)
            scores.append((candidate, similarity))
        
        # 按相似度排序，返回top_k个结果
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def entity_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """实体相似度"""
        similarities = []
        
        # 名称相似度
        name1 = entity1.get('name', '')
        name2 = entity2.get('name', '')
        name_sim = self.string_similarity(name1, name2)
        similarities.append(('name', name_sim, 0.4))
        
        # 类型相似度
        type1 = entity1.get('type', '')
        type2 = entity2.get('type', '')
        type_sim = 1.0 if type1 == type2 else 0.0
        similarities.append(('type', type_sim, 0.3))
        
        # 属性相似度
        props1 = entity1.get('properties', {})
        props2 = entity2.get('properties', {})
        props_sim = self.structural_similarity(props1, props2)
        similarities.append(('properties', props_sim, 0.2))
        
        # 别名相似度
        aliases1 = set(entity1.get('aliases', []))
        aliases2 = set(entity2.get('aliases', []))
        aliases_sim = len(aliases1 & aliases2) / len(aliases1 | aliases2) \
                     if (aliases1 | aliases2) else 0.0
        similarities.append(('aliases', aliases_sim, 0.1))
        
        # 加权平均
        weighted_sum = sum(sim * weight for _, sim, weight in similarities)
        return weighted_sum
    
    def relation_similarity(self, relation1: Dict[str, Any], relation2: Dict[str, Any]) -> float:
        """关系相似度"""
        similarities = []
        
        # 关系类型相似度
        type1 = relation1.get('type', '')
        type2 = relation2.get('type', '')
        type_sim = self.string_similarity(type1, type2)
        similarities.append(('type', type_sim, 0.5))
        
        # 头实体相似度
        head1 = relation1.get('head_entity', '')
        head2 = relation2.get('head_entity', '')
        head_sim = self.string_similarity(head1, head2)
        similarities.append(('head', head_sim, 0.25))
        
        # 尾实体相似度
        tail1 = relation1.get('tail_entity', '')
        tail2 = relation2.get('tail_entity', '')
        tail_sim = self.string_similarity(tail1, tail2)
        similarities.append(('tail', tail_sim, 0.25))
        
        # 加权平均
        weighted_sum = sum(sim * weight for _, sim, weight in similarities)
        return weighted_sum
    
    def batch_similarity_matrix(self, items: List[str], 
                               method: str = 'combined') -> List[List[float]]:
        """批量计算相似度矩阵"""
        n = len(items)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    similarity = 1.0
                else:
                    similarity = self.string_similarity(items[i], items[j], method)
                
                matrix[i][j] = similarity
                matrix[j][i] = similarity  # 对称矩阵
        
        return matrix
    
    def find_duplicates(self, items: List[str], threshold: float = 0.8) -> List[List[int]]:
        """找出重复项（相似度超过阈值的项）"""
        similarity_matrix = self.batch_similarity_matrix(items)
        n = len(items)
        
        duplicates = []
        visited = set()
        
        for i in range(n):
            if i in visited:
                continue
            
            duplicate_group = [i]
            for j in range(i + 1, n):
                if similarity_matrix[i][j] >= threshold:
                    duplicate_group.append(j)
                    visited.add(j)
            
            if len(duplicate_group) > 1:
                duplicates.append(duplicate_group)
            
            visited.add(i)
        
        return duplicates
    
    def clustering_by_similarity(self, items: List[str], 
                                threshold: float = 0.7) -> List[List[int]]:
        """基于相似度的聚类"""
        similarity_matrix = self.batch_similarity_matrix(items)
        n = len(items)
        
        clusters = []
        visited = set()
        
        def dfs(node: int, cluster: List[int]):
            visited.add(node)
            cluster.append(node)
            
            for neighbor in range(n):
                if (neighbor not in visited and 
                    similarity_matrix[node][neighbor] >= threshold):
                    dfs(neighbor, cluster)
        
        for i in range(n):
            if i not in visited:
                cluster = []
                dfs(i, cluster)
                clusters.append(cluster)
        
        return clusters