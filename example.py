#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例：获取不同YouTube频道的视频信息
"""

import os
from youtube_video_fetcher import YouTubeVideoFetcher

def get_api_key():
    """从环境变量获取API密钥"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ 请设置环境变量 YOUTUBE_API_KEY")
        print("设置方法:")
        print("  Linux/Mac: export YOUTUBE_API_KEY='你的API密钥'")
        print("  Windows: set YOUTUBE_API_KEY=你的API密钥")
        print("  PowerShell: $env:YOUTUBE_API_KEY='你的API密钥'")
        return None
    return api_key

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 从环境变量获取API密钥
    API_KEY = get_api_key()
    if not API_KEY:
        return
    
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    # 李永乐老师频道
    channel_id = 'UCMUnInmOkrWN4gof9KlhNmQ'
    
    print(f"正在获取频道 {channel_id} 的视频...")
    video_data = fetcher.get_channel_videos(channel_id, max_videos=10)  # 限制获取10个
    
    if video_data:
        print(f"\n成功获取 {len(video_data)} 个视频!")
        
        # 显示视频信息
        for i, video in enumerate(video_data, 1):
            print(f"{i}. {video['title']}")
            print(f"   视频ID: {video['video_id']}")
            print(f"   发布时间: {video['published_at']}")
            print(f"   视频链接: https://www.youtube.com/watch?v={video['video_id']}")
            print()
    else:
        print("未能获取到视频数据")

def example_multiple_formats():
    """多格式保存示例"""
    print("=== 多格式保存示例 ===")
    
    # 从环境变量获取API密钥
    API_KEY = get_api_key()
    if not API_KEY:
        return
    
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    # 获取少量视频用于演示
    channel_id = 'UCMUnInmOkrWN4gof9KlhNmQ'
    video_data = fetcher.get_channel_videos(channel_id, max_videos=5)
    
    if video_data:
        # 保存为不同格式
        fetcher.save_to_file(video_data, 'example_ids.txt', 'txt')
        fetcher.save_to_file(video_data, 'example_videos.json', 'json')
        fetcher.save_to_file(video_data, 'example_videos.csv', 'csv')
        
        print("已保存为三种格式:")
        print("- example_ids.txt (纯视频ID)")
        print("- example_videos.json (完整JSON数据)")
        print("- example_videos.csv (CSV表格格式)")

def example_different_channels():
    """不同频道示例"""
    print("=== 不同频道示例 ===")
    
    # 从环境变量获取API密钥
    API_KEY = get_api_key()
    if not API_KEY:
        return
    
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    # 一些知名的YouTube频道ID（示例）
    channels = {
        '李永乐老师': 'UCMUnInmOkrWN4gof9KlhNmQ',
        # 可以添加其他频道ID
        # 'TED': 'UCAuUUnT6oDeKwE6v1NGQxug',
        # '国家地理': 'UCpVm7bg6pXKo1Pr6k5kxG9A'
    }
    
    for channel_name, channel_id in channels.items():
        print(f"\n正在获取 {channel_name} 频道的视频信息...")
        video_data = fetcher.get_channel_videos(channel_id, max_videos=3)
        
        if video_data:
            print(f"成功获取 {len(video_data)} 个视频:")
            for video in video_data:
                print(f"  - {video['title']}")
        else:
            print(f"获取 {channel_name} 频道失败")

def example_error_handling():
    """错误处理示例"""
    print("=== 错误处理示例 ===")
    
    # 使用无效的API密钥进行错误演示
    fetcher = YouTubeVideoFetcher('INVALID_API_KEY')
    
    channel_id = 'UCMUnInmOkrWN4gof9KlhNmQ'
    print("使用无效API密钥测试错误处理...")
    
    video_data = fetcher.get_channel_videos(channel_id, max_videos=1)
    
    if not video_data:
        print("如预期，使用无效API密钥无法获取数据")
        print("请确保使用有效的YouTube Data API v3密钥")
        print("并通过环境变量 YOUTUBE_API_KEY 设置")

if __name__ == "__main__":
    print("YouTube视频获取工具使用示例")
    print("🔑 现在使用环境变量 YOUTUBE_API_KEY 获取API密钥\n")
    
    # 运行示例（现在使用环境变量）
    # example_basic_usage()
    # example_multiple_formats()
    # example_different_channels()
    example_error_handling()
    
    print("\n示例结束。更多使用方法请参考 README.md")
