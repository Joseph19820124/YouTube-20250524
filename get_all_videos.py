#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取完整频道数据示例
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

def get_all_channel_videos():
    """获取频道的所有视频"""
    print("=== 获取完整频道数据 ===")
    
    # 从环境变量获取API密钥
    API_KEY = get_api_key()
    if not API_KEY:
        return
    
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    # 李永乐老师频道
    channel_id = 'UCWZwfV3ICOt3uEPpW6hYK4g'
    
    print(f"正在获取频道 {channel_id} 的所有视频...")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    # 获取所有视频（不设置max_videos限制）
    video_data = fetcher.get_channel_videos(channel_id)
    
    if video_data:
        print(f"\n🎉 成功获取 {len(video_data)} 个视频!")
        
        # 显示统计信息
        print(f"\n📊 统计信息:")
        print(f"- 总视频数量: {len(video_data)}")
        print(f"- 最新视频: {video_data[0]['title']}")
        print(f"- 最早视频: {video_data[-1]['title']}")
        
        # 保存为不同格式
        print(f"\n💾 保存文件...")
        fetcher.save_to_file(video_data, 'liyongle_all_video_ids.txt', 'txt')
        fetcher.save_to_file(video_data, 'liyongle_all_videos.json', 'json')
        fetcher.save_to_file(video_data, 'liyongle_all_videos.csv', 'csv')
        
        print("\n✅ 所有数据已保存为:")
        print("- liyongle_all_video_ids.txt (纯视频ID列表)")
        print("- liyongle_all_videos.json (完整JSON数据)")
        print("- liyongle_all_videos.csv (CSV表格格式)")
        
        # 显示前5个和最后5个视频作为预览
        print(f"\n🔍 最新5个视频预览:")
        for i, video in enumerate(video_data[:5], 1):
            print(f"{i}. {video['title']} ({video['published_at'][:10]})")
        
        print(f"\n🔍 最早5个视频预览:")
        for i, video in enumerate(video_data[-5:], len(video_data)-4):
            print(f"{i}. {video['title']} ({video['published_at'][:10]})")
            
    else:
        print("❌ 未能获取到视频数据，请检查API密钥是否正确")

def get_recent_videos(count=50):
    """获取最近的N个视频"""
    print(f"=== 获取最近 {count} 个视频 ===")
    
    # 从环境变量获取API密钥
    API_KEY = get_api_key()
    if not API_KEY:
        return
    
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    channel_id = 'UCWZwfV3ICOt3uEPpW6hYK4g'
    
    print(f"正在获取频道最近的 {count} 个视频...")
    video_data = fetcher.get_channel_videos(channel_id, max_videos=count)
    
    if video_data:
        print(f"\n✅ 成功获取 {len(video_data)} 个视频!")
        
        # 保存数据
        fetcher.save_to_file(video_data, f'liyongle_recent_{count}_videos.json', 'json')
        
        # 显示视频列表
        print(f"\n📋 最近 {len(video_data)} 个视频:")
        for i, video in enumerate(video_data, 1):
            print(f"{i:2d}. {video['title']}")
            print(f"    发布时间: {video['published_at'][:10]}")
            print(f"    视频链接: https://www.youtube.com/watch?v={video['video_id']}")
            print()
        
        print(f"💾 数据已保存到: liyongle_recent_{count}_videos.json")
    else:
        print("❌ 未能获取到视频数据")

if __name__ == "__main__":
    print("YouTube频道完整数据获取工具")
    print("🔑 现在使用环境变量 YOUTUBE_API_KEY 获取API密钥\n")
    
    choice = input("选择操作:\n1. 获取所有视频\n2. 获取最近50个视频\n3. 获取最近100个视频\n请输入选择 (1-3): ").strip()
    
    if choice == '1':
        get_all_channel_videos()
    elif choice == '2':
        get_recent_videos(50)
    elif choice == '3':
        get_recent_videos(100)
    else:
        print("无效选择，获取最近50个视频...")
        get_recent_videos(50)
    
    print("\n🎉 操作完成!")
