"""
配置管理模块
"""
import os
import json
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ExtractionConfig:
    """抽取配置"""
    similarity_threshold: float = 0.8
    min_entity_length: int = 2
    min_confidence: float = 0.5
    max_context_window: int = 50
    use_patterns: bool = True
    use_pos_tagging: bool = True
    use_dictionary: bool = True


@dataclass
class MappingConfig:
    """映射配置"""
    entity_similarity_threshold: float = 0.8
    relation_similarity_threshold: float = 0.7
    fuzzy_match_threshold: float = 0.6
    use_semantic_mapping: bool = True
    use_context_mapping: bool = True


@dataclass
class FusionConfig:
    """融合配置"""
    entity_fusion_threshold: float = 0.8
    relation_fusion_threshold: float = 0.8
    conflict_resolution_strategy: str = "highest_confidence"
    merge_similar_entities: bool = True
    preserve_provenance: bool = True


@dataclass
class VisualizationConfig:
    """可视化配置"""
    max_nodes: int = 50
    node_size: int = 500
    edge_width: float = 1.0
    layout: str = "spring"
    output_format: str = "png"
    figure_size: tuple = (12, 8)


class Config:
    """配置管理器"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "kg_demo/config/default_config.json"
        
        # 默认配置
        self.extraction = ExtractionConfig()
        self.mapping = MappingConfig()
        self.fusion = FusionConfig()
        self.visualization = VisualizationConfig()
        
        # 其他配置
        self.output_dir = "kg_demo/output"
        self.data_dir = "kg_demo/data"
        self.log_level = "INFO"
        self.enable_caching = True
        self.cache_dir = "kg_demo/cache"
        
        # 如果配置文件存在，加载配置
        if os.path.exists(self.config_file):
            self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 更新各个配置段
            if 'extraction' in config_data:
                self._update_config(self.extraction, config_data['extraction'])
            
            if 'mapping' in config_data:
                self._update_config(self.mapping, config_data['mapping'])
            
            if 'fusion' in config_data:
                self._update_config(self.fusion, config_data['fusion'])
            
            if 'visualization' in config_data:
                self._update_config(self.visualization, config_data['visualization'])
            
            # 更新其他配置
            for key in ['output_dir', 'data_dir', 'log_level', 'enable_caching', 'cache_dir']:
                if key in config_data:
                    setattr(self, key, config_data[key])
                    
        except Exception as e:
            print(f"警告: 加载配置文件失败: {e}")
    
    def _update_config(self, config_obj: Any, config_dict: Dict[str, Any]):
        """更新配置对象"""
        for key, value in config_dict.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
    
    def save_config(self):
        """保存配置到文件"""
        config_data = {
            'extraction': asdict(self.extraction),
            'mapping': asdict(self.mapping),
            'fusion': asdict(self.fusion),
            'visualization': asdict(self.visualization),
            'output_dir': self.output_dir,
            'data_dir': self.data_dir,
            'log_level': self.log_level,
            'enable_caching': self.enable_caching,
            'cache_dir': self.cache_dir
        }
        
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_extraction_config(self) -> ExtractionConfig:
        """获取抽取配置"""
        return self.extraction
    
    def get_mapping_config(self) -> MappingConfig:
        """获取映射配置"""
        return self.mapping
    
    def get_fusion_config(self) -> FusionConfig:
        """获取融合配置"""
        return self.fusion
    
    def get_visualization_config(self) -> VisualizationConfig:
        """获取可视化配置"""
        return self.visualization
    
    def update_extraction_config(self, **kwargs):
        """更新抽取配置"""
        for key, value in kwargs.items():
            if hasattr(self.extraction, key):
                setattr(self.extraction, key, value)
    
    def update_mapping_config(self, **kwargs):
        """更新映射配置"""
        for key, value in kwargs.items():
            if hasattr(self.mapping, key):
                setattr(self.mapping, key, value)
    
    def update_fusion_config(self, **kwargs):
        """更新融合配置"""
        for key, value in kwargs.items():
            if hasattr(self.fusion, key):
                setattr(self.fusion, key, value)
    
    def update_visualization_config(self, **kwargs):
        """更新可视化配置"""
        for key, value in kwargs.items():
            if hasattr(self.visualization, key):
                setattr(self.visualization, key, value)
    
    def create_directories(self):
        """创建必要的目录"""
        directories = [
            self.output_dir,
            self.data_dir,
            self.cache_dir,
            os.path.dirname(self.config_file)
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                print(f"创建目录: {directory}")
    
    def print_config(self):
        """打印当前配置"""
        print("=" * 50)
        print("当前配置:")
        print("=" * 50)
        
        print("抽取配置:")
        for key, value in asdict(self.extraction).items():
            print(f"  {key}: {value}")
        
        print("\n映射配置:")
        for key, value in asdict(self.mapping).items():
            print(f"  {key}: {value}")
        
        print("\n融合配置:")
        for key, value in asdict(self.fusion).items():
            print(f"  {key}: {value}")
        
        print("\n可视化配置:")
        for key, value in asdict(self.visualization).items():
            print(f"  {key}: {value}")
        
        print("\n其他配置:")
        print(f"  output_dir: {self.output_dir}")
        print(f"  data_dir: {self.data_dir}")
        print(f"  log_level: {self.log_level}")
        print(f"  enable_caching: {self.enable_caching}")
        print(f"  cache_dir: {self.cache_dir}")
        
        print("=" * 50)