#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将视频ID列表转换为Excel格式的工具
"""

import os
from youtube_video_fetcher import YouTubeVideoFetcher

def convert_video_ids_to_excel():
    """将video_ids.txt转换为Excel格式"""
    
    # 读取视频ID列表
    try:
        with open('video_ids.txt', 'r', encoding='utf-8') as f:
            video_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ 未找到 video_ids.txt 文件")
        return
    
    print(f"📖 读取了 {len(video_ids)} 个视频ID")
    
    # 创建Excel数据
    excel_data = []
    for i, video_id in enumerate(video_ids, 1):
        excel_data.append({
            '序号': i,
            '视频ID': video_id,
            'YouTube链接': f'https://www.youtube.com/watch?v={video_id}',
            '备注': ''
        })
    
    # 保存为CSV（Excel可以直接打开）
    import csv
    
    with open('youtube_videos.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['序号', '视频ID', 'YouTube链接', '备注'])
        writer.writeheader()
        writer.writerows(excel_data)
    
    print(f"✅ 已生成 youtube_videos.csv 文件，包含 {len(excel_data)} 个视频")
    print("💡 可以直接用Excel打开此CSV文件")

def fetch_video_details():
    """获取视频详细信息（需要API密钥）"""
    
    # 检查环境变量
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("⚠️  未设置 YOUTUBE_API_KEY 环境变量")
        print("   如需获取视频标题等详细信息，请设置API密钥")
        return
    
    # 读取视频ID列表
    try:
        with open('video_ids.txt', 'r', encoding='utf-8') as f:
            video_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ 未找到 video_ids.txt 文件")
        return
    
    print(f"🚀 开始获取 {len(video_ids)} 个视频的详细信息...")
    
    # 使用YouTube API获取详细信息
    fetcher = YouTubeVideoFetcher(api_key)
    
    # 这里可以添加获取视频详细信息的逻辑
    # 由于API限制，建议分批处理
    print("💡 由于API限制，建议使用现有的工具获取视频详细信息")
    print("   可以使用 get_all_videos.py 获取完整的视频信息")

if __name__ == "__main__":
    print("YouTube视频ID转换工具")
    print("=" * 40)
    
    choice = input("选择操作:\n1. 转换为CSV格式\n2. 获取视频详细信息\n请输入选择 (1-2): ").strip()
    
    if choice == '1':
        convert_video_ids_to_excel()
    elif choice == '2':
        fetch_video_details()
    else:
        print("无效选择，执行CSV转换...")
        convert_video_ids_to_excel()
