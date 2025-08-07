"""
可视化工具模块 - 处理中文字体显示问题
"""
import matplotlib.pyplot as plt
import matplotlib
import platform
import warnings
warnings.filterwarnings('ignore')


class ChineseFontManager:
    """中文字体管理器"""
    
    def __init__(self):
        self.font_configured = False
        self.available_font = None
        self.setup_font()
    
    def setup_font(self):
        """设置中文字体"""
        system = platform.system()
        
        # 根据操作系统选择字体
        font_candidates = []
        
        if system == "Darwin":  # macOS
            font_candidates = [
                'Arial Unicode MS',
                'Helvetica Neue', 
                'STHeiti',
                'Hiragino Sans GB',
                'PingFang SC',
                'SimHei',
                'DejaVu Sans'
            ]
        elif system == "Windows":
            font_candidates = [
                'Microsoft YaHei',
                'SimHei',
                'KaiTi',
                'FangSong',
                'STSong'
            ]
        else:  # Linux
            font_candidates = [
                'Noto Sans CJK SC',
                'WenQuanYi Micro Hei',
                'Source Han Sans SC',
                'DejaVu Sans'
            ]
        
        # 测试字体可用性
        for font_name in font_candidates:
            if self.test_font(font_name):
                self.available_font = font_name
                self.configure_matplotlib(font_name)
                self.font_configured = True
                print(f"✅ 使用字体: {font_name}")
                break
        
        if not self.font_configured:
            print("⚠️  未找到合适的中文字体，将使用英文显示")
            self.configure_matplotlib('DejaVu Sans')
            self.available_font = 'DejaVu Sans'
    
    def test_font(self, font_name: str) -> bool:
        """测试字体是否可用"""
        try:
            import warnings
            from matplotlib.font_manager import fontManager
            
            # 抑制所有字体相关警告
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # 简单测试：检查字体是否在系统字体列表中
                available_fonts = [f.name for f in fontManager.ttflist]
                if font_name in available_fonts:
                    return True
                
                # 备用测试：尝试使用字体创建图像
                fig, ax = plt.subplots(figsize=(1, 1))
                try:
                    # 设置字体并创建文本
                    ax.text(0.5, 0.5, 'Test 测试', fontfamily=font_name, fontsize=10)
                    
                    # 如果没有异常，认为字体可用
                    plt.close(fig)
                    return True
                except:
                    plt.close(fig)
                    return False
                
        except Exception:
            return False
    
    def configure_matplotlib(self, font_name: str):
        """配置matplotlib字体"""
        try:
            plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['font.size'] = 10
        except Exception as e:
            print(f"字体配置失败: {e}")
    
    def get_font_properties(self, size: int = 10):
        """获取字体属性"""
        from matplotlib.font_manager import FontProperties
        return FontProperties(family=self.available_font, size=size)
    
    def safe_text(self, text: str) -> str:
        """安全的文本处理，避免字体不支持的字符"""
        if not self.font_configured or self.available_font == 'DejaVu Sans':
            # 如果没有中文字体，将中文转换为英文或拼音
            return self.chinese_to_english(text)
        return text
    
    def chinese_to_english(self, text: str) -> str:
        """简单的中文到英文映射"""
        chinese_to_english_map = {
            '知识图谱可视化': 'Knowledge Graph Visualization',
            '实体': 'entities',
            '关系': 'relations',
            '张三': 'Zhang San',
            '李四': 'Li Si',
            '王五': 'Wang Wu',
            '北京大学': 'Peking University',
            '腾讯公司': 'Tencent',
            '阿里巴巴': 'Alibaba',
            '苹果公司': 'Apple Inc',
            '微软公司': 'Microsoft',
            '谷歌公司': 'Google',
            '上海交通大学': 'SJTU',
            '斯坦福大学': 'Stanford',
            '中国科学院': 'CAS',
            '深圳市': 'Shenzhen',
            '北京市': 'Beijing',
            '杭州市': 'Hangzhou',
            '上海市': 'Shanghai',
            '马云': 'Jack Ma',
            '比尔·盖茨': 'Bill Gates',
            '史蒂夫·乔布斯': 'Steve Jobs',
            '微信': 'WeChat',
            'iPhone': 'iPhone',
            '淘宝': 'Taobao',
            'Windows': 'Windows'
        }
        
        # 替换已知的中文词汇
        result = text
        for chinese, english in chinese_to_english_map.items():
            result = result.replace(chinese, english)
        
        # 如果还有中文字符，尝试简化处理
        if any('\u4e00' <= char <= '\u9fff' for char in result):
            # 保留英文和数字，其他字符用_代替
            result = ''.join(char if char.isalnum() or char in ' .,()[]' else '_' 
                           for char in result)
        
        return result


# 全局字体管理器实例
font_manager = ChineseFontManager()


def setup_chinese_display():
    """设置中文显示（向后兼容）"""
    return font_manager


def get_display_text(text: str) -> str:
    """获取适合显示的文本"""
    return font_manager.safe_text(text)


def create_title(entities_count: int, relations_count: int) -> str:
    """创建图表标题"""
    if font_manager.font_configured and font_manager.available_font != 'DejaVu Sans':
        return f"知识图谱可视化 ({entities_count} 实体, {relations_count} 关系)"
    else:
        return f"Knowledge Graph ({entities_count} entities, {relations_count} relations)"