#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的演示运行脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_core.main import KnowledgeGraphDemo


def main():
    """简化的演示入口"""
    print("🎯 知识图谱构建演示")
    print("=" * 50)
    
    # 创建演示实例
    demo = KnowledgeGraphDemo()
    
    # 运行完整演示
    result = demo.run_complete_demo()
    
    if result:
        print("\n🎉 演示成功完成!")
        print("📁 请查看 kg_core/output/ 目录下的输出文件")
    else:
        print("\n❌ 演示过程中出现错误")


if __name__ == "__main__":
    main()