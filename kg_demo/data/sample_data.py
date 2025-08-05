"""
示例数据生成器 - 提供用于演示的示例文本和实体数据
"""
from typing import List, Dict
import uuid
from ..entity_definition.entity_types import Entity
from ..entity_definition.relation_types import Relation


class SampleDataGenerator:
    """示例数据生成器"""
    
    def __init__(self):
        self.sample_texts = self._create_sample_texts()
        self.sample_entities = self._create_sample_entities()
        self.sample_relations = self._create_sample_relations()
    
    def _create_sample_texts(self) -> List[str]:
        """创建示例文本"""
        texts = [
            """
            张三是北京大学的教授，专门研究人工智能领域。他在2010年创立了智能科技公司，
            该公司位于北京市海淀区中关村。张三教授发表了多篇关于机器学习的重要论文，
            并且经常参加国际学术会议。他的研究团队开发了一个名为"智能助手"的AI系统。
            """,
            
            """
            李四是腾讯公司的高级工程师，主要负责微信产品的开发工作。腾讯公司成立于1998年，
            总部设在深圳市南山区。李四毕业于清华大学计算机科学与技术专业，
            在加入腾讯之前曾在阿里巴巴工作了三年。他参与开发了微信支付功能。
            """,
            
            """
            王五是上海交通大学的博士生，他的导师是陈教授。王五的研究方向是深度学习，
            特别关注计算机视觉领域。他曾在谷歌实习了六个月，参与了TensorFlow项目的开发。
            王五发表了5篇顶级会议论文，包括CVPR和ICCV。
            """,
            
            """
            阿里巴巴集团由马云创建于1999年，总部位于杭州市西湖区。阿里巴巴旗下有淘宝、
            天猫、支付宝等知名产品。公司在纽约证券交易所上市，是中国最大的电商平台。
            阿里云是阿里巴巴的云计算业务，为全球企业提供云服务。
            """,
            
            """
            苹果公司由史蒂夫·乔布斯创立于1976年，总部位于美国加利福尼亚州库比蒂诺。
            苹果公司推出了iPhone、iPad、MacBook等革命性产品。蒂姆·库克现任苹果公司CEO，
            他在2011年接替乔布斯成为公司领导者。苹果公司是全球市值最高的科技公司之一。
            """,
            
            """
            OpenAI是一家人工智能研究公司，由萨姆·奥特曼等人创立。公司开发了GPT系列模型，
            包括GPT-3和GPT-4，这些模型在自然语言处理领域取得了突破性进展。OpenAI还推出了
            ChatGPT聊天机器人，该产品在全球范围内获得了巨大成功。
            """,
            
            """
            中国科学院是中国最高学术机构，成立于1949年，院部位于北京市。中科院下属多个研究所，
            包括计算技术研究所、自动化研究所等。许多知名科学家都曾在中科院工作，
            为中国科技发展做出了重要贡献。中科院在人工智能、量子计算等前沿领域有重要突破。
            """,
            
            """
            斯坦福大学位于美国加利福尼亚州帕洛阿尔托，是世界顶级私立研究型大学。
            该校在人工智能领域享有盛誉，李飞飞教授曾担任斯坦福AI实验室主任。
            斯坦福大学培养了众多科技企业家，包括谷歌创始人拉里·佩奇和谢尔盖·布林。
            """,
            
            """
            谷歌公司由拉里·佩奇和谢尔盖·布林创立于1998年，总部位于美国加州山景城。
            谷歌开发了世界上最流行的搜索引擎，并推出了Android操作系统。
            谷歌的母公司Alphabet旗下还包括YouTube、Gmail等产品。公司在AI领域投入巨大，
            开发了AlphaGo、BERT等知名AI系统。
            """,
            
            """
            微软公司由比尔·盖茨和保罗·艾伦创立于1975年，总部位于美国华盛顿州雷德蒙德。
            微软开发了Windows操作系统和Office办公套件，这些产品被全球数十亿用户使用。
            萨蒂亚·纳德拉现任微软CEO，他推动了公司向云计算和AI领域的转型。
            """
        ]
        
        return [text.strip() for text in texts]
    
    def _create_sample_entities(self) -> List[Entity]:
        """创建示例实体"""
        entities = []
        
        # 人物实体
        people = [
            ("张三", "北京大学教授，AI专家", {"occupation": "教授", "field": "人工智能"}),
            ("李四", "腾讯高级工程师", {"occupation": "工程师", "company": "腾讯"}),
            ("王五", "上海交通大学博士生", {"occupation": "学生", "degree": "博士"}),
            ("马云", "阿里巴巴创始人", {"occupation": "企业家", "company": "阿里巴巴"}),
            ("史蒂夫·乔布斯", "苹果公司创始人", {"occupation": "企业家", "company": "苹果"}),
            ("蒂姆·库克", "苹果公司CEO", {"occupation": "CEO", "company": "苹果"}),
            ("萨姆·奥特曼", "OpenAI创始人", {"occupation": "企业家", "company": "OpenAI"}),
            ("李飞飞", "斯坦福AI实验室前主任", {"occupation": "教授", "field": "人工智能"}),
            ("拉里·佩奇", "谷歌创始人", {"occupation": "企业家", "company": "谷歌"}),
            ("谢尔盖·布林", "谷歌创始人", {"occupation": "企业家", "company": "谷歌"}),
            ("比尔·盖茨", "微软创始人", {"occupation": "企业家", "company": "微软"}),
            ("萨蒂亚·纳德拉", "微软CEO", {"occupation": "CEO", "company": "微软"})
        ]
        
        for name, desc, props in people:
            entity = Entity(
                id=f"person_{len(entities)}",
                name=name,
                type="Person",
                properties=props,
                aliases=[]
            )
            entities.append(entity)
        
        # 组织实体
        organizations = [
            ("北京大学", "中国顶级高等学府", {"type": "大学", "location": "北京"}),
            ("腾讯公司", "中国互联网巨头", {"type": "科技公司", "founded": "1998"}),
            ("上海交通大学", "中国著名大学", {"type": "大学", "location": "上海"}),
            ("阿里巴巴集团", "中国电商巨头", {"type": "科技公司", "founded": "1999"}),
            ("苹果公司", "美国科技公司", {"type": "科技公司", "founded": "1976"}),
            ("OpenAI", "人工智能研究公司", {"type": "AI公司", "focus": "人工智能研究"}),
            ("中国科学院", "中国最高学术机构", {"type": "科研院所", "founded": "1949"}),
            ("斯坦福大学", "美国顶级私立大学", {"type": "大学", "location": "美国加州"}),
            ("谷歌公司", "美国科技巨头", {"type": "科技公司", "founded": "1998"}),
            ("微软公司", "美国软件公司", {"type": "科技公司", "founded": "1975"})
        ]
        
        for name, desc, props in organizations:
            entity = Entity(
                id=f"org_{len(entities)}",
                name=name,
                type="Organization",
                properties=props,
                aliases=[]
            )
            entities.append(entity)
        
        # 地点实体
        locations = [
            ("北京市", "中国首都", {"type": "城市", "country": "中国"}),
            ("海淀区", "北京市区", {"type": "区", "city": "北京"}),
            ("深圳市", "中国经济特区", {"type": "城市", "country": "中国"}),
            ("杭州市", "浙江省省会", {"type": "城市", "country": "中国"}),
            ("上海市", "中国直辖市", {"type": "城市", "country": "中国"}),
            ("库比蒂诺", "苹果总部所在地", {"type": "城市", "country": "美国"}),
            ("山景城", "谷歌总部所在地", {"type": "城市", "country": "美国"}),
            ("雷德蒙德", "微软总部所在地", {"type": "城市", "country": "美国"})
        ]
        
        for name, desc, props in locations:
            entity = Entity(
                id=f"loc_{len(entities)}",
                name=name,
                type="Location",
                properties=props,
                aliases=[]
            )
            entities.append(entity)
        
        # 产品实体
        products = [
            ("iPhone", "苹果智能手机", {"type": "智能手机", "manufacturer": "苹果"}),
            ("微信", "腾讯即时通讯软件", {"type": "软件", "manufacturer": "腾讯"}),
            ("淘宝", "阿里巴巴购物平台", {"type": "电商平台", "manufacturer": "阿里巴巴"}),
            ("Windows", "微软操作系统", {"type": "操作系统", "manufacturer": "微软"}),
            ("ChatGPT", "OpenAI聊天机器人", {"type": "AI产品", "manufacturer": "OpenAI"}),
            ("TensorFlow", "谷歌机器学习框架", {"type": "软件框架", "manufacturer": "谷歌"}),
            ("Android", "谷歌移动操作系统", {"type": "操作系统", "manufacturer": "谷歌"})
        ]
        
        for name, desc, props in products:
            entity = Entity(
                id=f"prod_{len(entities)}",
                name=name,
                type="Product",
                properties=props,
                aliases=[]
            )
            entities.append(entity)
        
        return entities
    
    def _create_sample_relations(self) -> List[Relation]:
        """创建示例关系（基于实体名称）"""
        relations = []
        
        # 工作关系
        work_relations = [
            ("张三", "works_for", "北京大学"),
            ("李四", "works_for", "腾讯公司"),
            ("王五", "works_for", "上海交通大学"),
            ("蒂姆·库克", "works_for", "苹果公司"),
            ("萨姆·奥特曼", "works_for", "OpenAI"),
            ("李飞飞", "works_for", "斯坦福大学"),
            ("萨蒂亚·纳德拉", "works_for", "微软公司")
        ]
        
        for head, rel_type, tail in work_relations:
            relation = Relation(
                id=f"rel_{len(relations)}",
                type=rel_type,
                head_entity_id=head,  # 这里简化使用名称，实际应用中需要ID
                tail_entity_id=tail,
                properties={"source": "sample_data"},
                confidence=1.0
            )
            relations.append(relation)
        
        # 创立关系
        founder_relations = [
            ("马云", "founder_of", "阿里巴巴集团"),
            ("史蒂夫·乔布斯", "founder_of", "苹果公司"),
            ("拉里·佩奇", "founder_of", "谷歌公司"),
            ("谢尔盖·布林", "founder_of", "谷歌公司"),
            ("比尔·盖茨", "founder_of", "微软公司"),
            ("张三", "founder_of", "智能科技公司")
        ]
        
        for head, rel_type, tail in founder_relations:
            relation = Relation(
                id=f"rel_{len(relations)}",
                type=rel_type,
                head_entity_id=head,
                tail_entity_id=tail,
                properties={"source": "sample_data"},
                confidence=1.0
            )
            relations.append(relation)
        
        # 位置关系
        location_relations = [
            ("北京大学", "located_in", "北京市"),
            ("腾讯公司", "located_in", "深圳市"),
            ("阿里巴巴集团", "located_in", "杭州市"),
            ("苹果公司", "located_in", "库比蒂诺"),
            ("谷歌公司", "located_in", "山景城"),
            ("微软公司", "located_in", "雷德蒙德"),
            ("斯坦福大学", "located_in", "库比蒂诺")
        ]
        
        for head, rel_type, tail in location_relations:
            relation = Relation(
                id=f"rel_{len(relations)}",
                type=rel_type,
                head_entity_id=head,
                tail_entity_id=tail,
                properties={"source": "sample_data"},
                confidence=1.0
            )
            relations.append(relation)
        
        # 产品关系
        product_relations = [
            ("苹果公司", "produces", "iPhone"),
            ("腾讯公司", "produces", "微信"),
            ("阿里巴巴集团", "produces", "淘宝"),
            ("微软公司", "produces", "Windows"),
            ("OpenAI", "produces", "ChatGPT"),
            ("谷歌公司", "produces", "TensorFlow"),
            ("谷歌公司", "produces", "Android")
        ]
        
        for head, rel_type, tail in product_relations:
            relation = Relation(
                id=f"rel_{len(relations)}",
                type=rel_type,
                head_entity_id=head,
                tail_entity_id=tail,
                properties={"source": "sample_data"},
                confidence=1.0
            )
            relations.append(relation)
        
        return relations
    
    def get_sample_texts(self) -> List[str]:
        """获取示例文本"""
        return self.sample_texts
    
    def get_sample_entities(self) -> List[Entity]:
        """获取示例实体"""
        return self.sample_entities
    
    def get_sample_relations(self) -> List[Relation]:
        """获取示例关系"""
        return self.sample_relations
    
    def get_domain_specific_texts(self, domain: str) -> List[str]:
        """获取特定领域的示例文本"""
        domain_texts = {
            "technology": [
                text for text in self.sample_texts 
                if any(keyword in text for keyword in ["公司", "技术", "AI", "系统", "开发"])
            ],
            "academic": [
                text for text in self.sample_texts
                if any(keyword in text for keyword in ["大学", "教授", "研究", "博士", "论文"])
            ],
            "business": [
                text for text in self.sample_texts
                if any(keyword in text for keyword in ["创立", "CEO", "企业", "上市", "产品"])
            ]
        }
        
        return domain_texts.get(domain, self.sample_texts)
    
    def create_custom_entity(self, name: str, entity_type: str, 
                           properties: Dict = None, aliases: List[str] = None) -> Entity:
        """创建自定义实体"""
        return Entity(
            id=str(uuid.uuid4()),
            name=name,
            type=entity_type,
            properties=properties or {},
            aliases=aliases or []
        )
    
    def create_custom_relation(self, head_entity_id: str, relation_type: str,
                             tail_entity_id: str, properties: Dict = None,
                             confidence: float = 1.0) -> Relation:
        """创建自定义关系"""
        return Relation(
            id=str(uuid.uuid4()),
            type=relation_type,
            head_entity_id=head_entity_id,
            tail_entity_id=tail_entity_id,
            properties=properties or {},
            confidence=confidence
        )
    
    def print_sample_data_summary(self):
        """打印示例数据摘要"""
        print("📊 示例数据摘要:")
        print(f"  文本数量: {len(self.sample_texts)}")
        print(f"  实体数量: {len(self.sample_entities)}")
        print(f"  关系数量: {len(self.sample_relations)}")
        
        # 统计实体类型
        entity_types = {}
        for entity in self.sample_entities:
            entity_types[entity.type] = entity_types.get(entity.type, 0) + 1
        
        print(f"  实体类型分布:")
        for entity_type, count in entity_types.items():
            print(f"    {entity_type}: {count}")
        
        # 统计关系类型
        relation_types = {}
        for relation in self.sample_relations:
            relation_types[relation.type] = relation_types.get(relation.type, 0) + 1
        
        print(f"  关系类型分布:")
        for relation_type, count in relation_types.items():
            print(f"    {relation_type}: {count}")