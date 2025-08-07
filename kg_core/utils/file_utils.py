"""
文件工具模块
"""
import os
import json
import csv
import pickle
from typing import Any, List, Dict
import pandas as pd


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def ensure_dir(directory: str):
        """确保目录存在"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")
    
    @staticmethod
    def save_json(data: Any, filepath: str):
        """保存JSON文件"""
        FileUtils.ensure_dir(os.path.dirname(filepath))
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"JSON文件已保存: {filepath}")
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
    
    @staticmethod
    def load_json(filepath: str) -> Any:
        """加载JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
            return None
    
    @staticmethod
    def save_csv(data: List[Dict], filepath: str):
        """保存CSV文件"""
        FileUtils.ensure_dir(os.path.dirname(filepath))
        
        if not data:
            print("数据为空，无法保存CSV文件")
            return
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"CSV文件已保存: {filepath}")
        except Exception as e:
            print(f"保存CSV文件失败: {e}")
    
    @staticmethod
    def load_csv(filepath: str) -> pd.DataFrame:
        """加载CSV文件"""
        try:
            return pd.read_csv(filepath, encoding='utf-8')
        except Exception as e:
            print(f"加载CSV文件失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def save_pickle(data: Any, filepath: str):
        """保存pickle文件"""
        FileUtils.ensure_dir(os.path.dirname(filepath))
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            print(f"Pickle文件已保存: {filepath}")
        except Exception as e:
            print(f"保存Pickle文件失败: {e}")
    
    @staticmethod
    def load_pickle(filepath: str) -> Any:
        """加载pickle文件"""
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"加载Pickle文件失败: {e}")
            return None
    
    @staticmethod
    def save_text(text: str, filepath: str):
        """保存文本文件"""
        FileUtils.ensure_dir(os.path.dirname(filepath))
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"文本文件已保存: {filepath}")
        except Exception as e:
            print(f"保存文本文件失败: {e}")
    
    @staticmethod
    def load_text(filepath: str) -> str:
        """加载文本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"加载文本文件失败: {e}")
            return ""
    
    @staticmethod
    def list_files(directory: str, extension: str = None) -> List[str]:
        """列出目录中的文件"""
        if not os.path.exists(directory):
            return []
        
        files = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                if extension is None or filename.endswith(extension):
                    files.append(filepath)
        
        return files
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(filepath)
        except Exception:
            return 0
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(filepath) and os.path.isfile(filepath)
    
    @staticmethod
    def delete_file(filepath: str):
        """删除文件"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"文件已删除: {filepath}")
        except Exception as e:
            print(f"删除文件失败: {e}")
    
    @staticmethod
    def backup_file(filepath: str, backup_suffix: str = ".bak"):
        """备份文件"""
        if os.path.exists(filepath):
            backup_path = filepath + backup_suffix
            try:
                import shutil
                shutil.copy2(filepath, backup_path)
                print(f"文件已备份: {backup_path}")
                return backup_path
            except Exception as e:
                print(f"备份文件失败: {e}")
                return None
        return None
    
    @staticmethod
    def clean_directory(directory: str, keep_extensions: List[str] = None):
        """清理目录"""
        if not os.path.exists(directory):
            return
        
        keep_extensions = keep_extensions or []
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                if not any(filename.endswith(ext) for ext in keep_extensions):
                    try:
                        os.remove(filepath)
                        print(f"已删除: {filepath}")
                    except Exception as e:
                        print(f"删除文件失败 {filepath}: {e}")
    
    @staticmethod
    def create_file_index(directory: str) -> Dict[str, Dict]:
        """创建文件索引"""
        index = {}
        
        if not os.path.exists(directory):
            return index
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, directory)
                
                index[relative_path] = {
                    'absolute_path': filepath,
                    'size': FileUtils.get_file_size(filepath),
                    'extension': os.path.splitext(filename)[1],
                    'directory': os.path.dirname(relative_path)
                }
        
        return index