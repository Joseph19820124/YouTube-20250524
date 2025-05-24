#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义测试脚本
"""

from example import (
    example_basic_usage,
    example_multiple_formats, 
    example_different_channels,
    example_error_handling
)

def main():
    """运行特定的示例函数"""
    
    print("选择要运行的示例:")
    print("1. 基础使用示例")
    print("2. 多格式保存示例") 
    print("3. 不同频道示例")
    print("4. 错误处理示例")
    print("5. 运行所有示例")
    
    choice = input("\n请输入选择 (1-5): ").strip()
    
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
