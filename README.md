# 知识图谱构建演示项目

本项目是一个完整的知识图谱构建演示系统，展示了知识图谱构建的四个主要步骤：**主体定义**、**知识抽取**、**知识映射**、**知识融合**。

## 🎯 项目概述

知识图谱构建是一个复杂的过程，本项目通过模块化的设计和实际可运行的代码，演示了如何从原始文本数据构建出结构化的知识图谱。

### 🏗️ 四大核心模块

1. **主体定义 (Entity Definition)** - 定义本体结构、实体类型和关系类型
2. **知识抽取 (Knowledge Extraction)** - 从文本中抽取实体和关系
3. **知识映射 (Knowledge Mapping)** - 将抽取的知识映射到标准本体
4. **知识融合 (Knowledge Fusion)** - 合并多源知识，解决冲突

## 📁 项目结构

```
knowledge-graph-projects/
├── kg_demo/                          # 主项目目录
│   ├── entity_definition/            # 主体定义模块
│   │   ├── ontology.py              # 本体管理
│   │   ├── entity_types.py          # 实体类型管理
│   │   └── relation_types.py        # 关系类型管理
│   ├── knowledge_extraction/         # 知识抽取模块
│   │   ├── text_extractor.py        # 文本预处理
│   │   ├── entity_extractor.py      # 实体抽取
│   │   ├── relation_extractor.py    # 关系抽取
│   │   └── pattern_extractor.py     # 模式学习
│   ├── knowledge_mapping/            # 知识映射模块
│   │   ├── entity_mapper.py         # 实体映射
│   │   ├── relation_mapper.py       # 关系映射
│   │   ├── ontology_mapper.py       # 本体映射
│   │   └── similarity_calculator.py # 相似度计算
│   ├── knowledge_fusion/             # 知识融合模块
│   │   ├── entity_fusion.py         # 实体融合
│   │   ├── relation_fusion.py       # 关系融合
│   │   ├── conflict_resolution.py   # 冲突解决
│   │   └── knowledge_graph.py       # 知识图谱构建
│   ├── data/                         # 数据模块
│   │   └── sample_data.py           # 示例数据生成
│   ├── utils/                        # 工具模块
│   │   ├── logger.py                # 日志工具
│   │   ├── config.py                # 配置管理
│   │   └── file_utils.py            # 文件工具
│   ├── main.py                       # 主程序入口
│   └── requirements.txt              # 项目依赖
└── README.md                         # 项目说明
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 推荐使用虚拟环境

### 安装依赖

```bash
cd knowledge-graph-projects
pip install -r kg_demo/requirements.txt
```

### 运行演示

```bash
# 运行完整演示
python kg_demo/main.py

# 运行交互式演示
python kg_demo/main.py --mode interactive

# 只运行特定步骤
python kg_demo/main.py --step 1  # 主体定义
python kg_demo/main.py --step 2  # 知识抽取
```

## 📖 详细说明

### 1. 主体定义 (Entity Definition)

定义知识图谱的本体结构，包括：
- **实体类型**: Person, Organization, Location, Product, Event 等
- **关系类型**: works_for, located_in, founder_of 等
- **属性定义**: 每种实体和关系的属性模式

```python
from kg_demo.entity_definition.ontology import Ontology

# 创建本体
ontology = Ontology()
ontology.print_ontology_summary()
```

### 2. 知识抽取 (Knowledge Extraction)

从非结构化文本中抽取结构化知识：

- **文本预处理**: 分词、词性标注、关键词提取
- **实体识别**: 基于规则、统计和语义的实体抽取
- **关系抽取**: 模式匹配、依存句法、语义推理
- **模式学习**: 自动发现新的抽取模式

```python
from kg_demo.knowledge_extraction.entity_extractor import EntityExtractor
from kg_demo.knowledge_extraction.relation_extractor import RelationExtractor

entity_extractor = EntityExtractor()
relation_extractor = RelationExtractor()

# 抽取实体和关系
entities = entity_extractor.extract_entities(text)
relations = relation_extractor.extract_relations(text, entities)
```

### 3. 知识映射 (Knowledge Mapping)

将抽取的知识映射到标准本体：

- **实体映射**: 精确匹配、模糊匹配、语义匹配
- **关系映射**: 基于实体类型和上下文的关系推断
- **本体对齐**: 不同本体间的概念映射
- **相似度计算**: 多种字符串和语义相似度算法

```python
from kg_demo.knowledge_mapping.entity_mapper import EntityMapper
from kg_demo.knowledge_mapping.relation_mapper import RelationMapper

entity_mapper = EntityMapper()
relation_mapper = RelationMapper(ontology)

# 映射实体和关系
entity_mappings = entity_mapper.batch_map_entities(extracted_entities)
relation_mappings = relation_mapper.batch_map_relations(extracted_relations)
```

### 4. 知识融合 (Knowledge Fusion)

合并多源知识，构建一致的知识图谱：

- **实体融合**: 识别和合并重复实体
- **关系融合**: 去重和合并关系信息
- **冲突检测**: 发现知识间的不一致
- **冲突解决**: 基于置信度、时效性等策略解决冲突

```python
from kg_demo.knowledge_fusion.knowledge_graph import KnowledgeGraph
from kg_demo.knowledge_fusion.entity_fusion import EntityFusion
from kg_demo.knowledge_fusion.relation_fusion import RelationFusion

# 构建知识图谱
kg = KnowledgeGraph(ontology)
entity_fusion = EntityFusion()
relation_fusion = RelationFusion()

# 融合知识
entity_results = entity_fusion.batch_fuse_entities(entities)
relation_results = relation_fusion.batch_fuse_relations(relations)
```

## 🎨 功能特性

### 核心功能

- ✅ **完整的知识图谱构建流水线**
- ✅ **模块化设计，易于扩展**
- ✅ **支持中英文文本处理**
- ✅ **多种实体和关系抽取方法**
- ✅ **智能的知识映射和融合**
- ✅ **可视化知识图谱**
- ✅ **多种输出格式 (JSON, CSV, 图像)**

### 技术特色

- 🔧 **可配置的抽取参数**
- 🎯 **多策略的冲突解决**
- 📊 **详细的统计和评估**
- 🔍 **交互式演示模式**
- 📝 **完整的日志记录**
- 💾 **支持数据持久化**

## 📊 输出结果

运行完成后，系统会在 `kg_demo/output/` 目录下生成：

- `knowledge_graph.json` - 知识图谱JSON格式
- `entities.csv` - 实体表格
- `relations.csv` - 关系表格
- `knowledge_graph_visualization.png` - 可视化图像
- `ontology.json` - 本体定义

## 🔧 配置说明

可以通过修改配置来调整系统行为：

```python
from kg_demo.utils.config import Config

config = Config()
config.update_extraction_config(
    similarity_threshold=0.8,
    min_confidence=0.6
)
config.save_config()
```

## 📈 示例结果

使用项目内置的示例数据，系统能够：

- 从10段中文文本中抽取出50+个实体
- 识别出30+个关系
- 构建包含人物、组织、地点、产品等多类型实体的知识图谱
- 自动解决实体重复和关系冲突问题

## 🤝 扩展开发

### 添加新的实体类型

```python
from kg_demo.entity_definition.ontology import EntityType

new_entity_type = EntityType(
    name="Book",
    description="书籍实体",
    properties=["title", "author", "isbn", "publish_year"]
)
ontology.add_entity_type(new_entity_type)
```

### 添加新的抽取规则

```python
from kg_demo.knowledge_extraction.entity_extractor import EntityExtractor

extractor = EntityExtractor()
# 添加新的实体模式
extractor.entity_patterns["Book"] = [
    r'《[\u4e00-\u9fa5]+》',  # 中文书名
    r'"[A-Za-z\s]+"'         # 英文书名
]
```

### 自定义融合策略

```python
from kg_demo.knowledge_fusion.entity_fusion import EntityFusion

fusion = EntityFusion()
# 修改融合规则
fusion.fusion_rules["name_selection"]["strategy"] = "custom"
```

## 📚 技术文档

- [实体定义模块说明](docs/entity_definition.md) *(待添加)*
- [知识抽取算法详解](docs/knowledge_extraction.md) *(待添加)*
- [映射算法原理](docs/knowledge_mapping.md) *(待添加)*
- [融合策略详解](docs/knowledge_fusion.md) *(待添加)*

## 🐛 常见问题

### Q: 如何处理大规模文本数据？
A: 可以通过批处理和缓存机制来处理大规模数据，系统支持分批处理和结果缓存。

### Q: 如何提高抽取准确率？
A: 可以通过以下方式：
- 扩充实体词典
- 优化抽取规则
- 调整置信度阈值
- 增加领域特定的模式

### Q: 如何添加新的语言支持？
A: 需要：
- 添加对应语言的分词器
- 更新实体识别规则
- 调整文本预处理逻辑

## 📄 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。

## 🔗 相关资源

- [知识图谱技术与应用](https://example.com)
- [自然语言处理基础](https://example.com)
- [图数据库Neo4j](https://neo4j.com)
- [NetworkX图处理库](https://networkx.org)

## 📞 联系方式

如有问题或建议，请联系：
- 邮箱: your-email@example.com
- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！