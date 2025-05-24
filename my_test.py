#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义测试脚本
"""

import os
from example import (
    example_basic_usage,
    example_multiple_formats, 
    example_different_channels,
    example_error_handling
)

def check_api_key():
    """检查环境变量中的API密钥"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if api_key:
        print(f"✅ 环境变量 YOUTUBE_API_KEY 已设置 (前缀: {api_key[:10]}...)")
        return True
    else:
        print("❌ 环境变量 YOUTUBE_API_KEY 未设置")
        print("设置方法:")
        print("  Linux/Mac: export YOUTUBE_API_KEY='你的API密钥'")
        print("  Windows: set YOUTUBE_API_KEY=你的API密钥")
        print("  PowerShell: $env:YOUTUBE_API_KEY='你的API密钥'")
        return False

def main():
    """运行特定的示例函数"""
    
    print("YouTube视频获取工具 - 交互式测试")
    print("🔑 现在使用环境变量 YOUTUBE_API_KEY 获取API密钥\n")
    
    # 检查API密钥
    if not check_api_key():
        print("\n⚠️  可以先运行错误处理示例（不需要有效API密钥）")
    
    print("\n选择要运行的示例:")
    print("1. 基础使用示例")
    print("2. 多格式保存示例") 
    print("3. 不同频道示例")
    print("4. 错误处理示例 (无需API密钥)")
    print("5. 运行所有示例")
    
    choice = input("\n请输入选择 (1-5): ").strip()
    
    print("\n" + "="*60)
    
    if choice == '1':
        example_basic_usage()
    elif choice == '2':
        example_multiple_formats()
    elif choice == '3':
        example_different_channels()
    elif choice == '4':
        example_error_handling()
    elif choice == '5':
        print("运行所有示例...\n")
        example_basic_usage()
        print("\n" + "="*50 + "\n")
        example_multiple_formats()
        print("\n" + "="*50 + "\n")
        example_different_channels()
        print("\n" + "="*50 + "\n")
        example_error_handling()
    else:
        print("无效选择，运行错误处理示例...")
        example_error_handling()

if __name__ == "__main__":
    main()
