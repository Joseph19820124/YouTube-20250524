#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取完整频道数据示例
"""

import os
import requests
import json
import time
from youtube_video_fetcher import YouTubeVideoFetcher

# 频道ID常量
LIYONGLE_CHANNEL_ID = 'UC3tDHsQFbLpajLE_Pp8IYww'  # 十七岁天才中单频道 @ShiQiSuiTianCaiZhongDan

# SRT API 配置
SRT_API_URL = 'https://lic.deepsrt.cc/webhook/get-srt-from-provider'

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

def request_srt_for_video(video_id, fetch_only=False):
    """为单个视频请求SRT字幕"""
    try:
        payload = {
            "youtube_id": video_id,
            "fetch_only": str(fetch_only).lower()
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(SRT_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json(), "status_code": response.status_code}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "response": response.text}
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求超时"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"请求异常: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"未知错误: {str(e)}"}

def batch_request_srt(video_data, max_requests=None, delay=1.0):
    """批量请求所有视频的SRT字幕"""
    if not video_data:
        print("❌ 没有视频数据")
        return
    
    total_videos = len(video_data)
    if max_requests:
        total_videos = min(total_videos, max_requests)
        video_data = video_data[:max_requests]
    
    print(f"\n🚀 开始批量请求SRT字幕...")
    print(f"📊 总共需要处理 {total_videos} 个视频")
    print(f"⏱️  请求间隔: {delay} 秒")
    print("=" * 50)
    
    results = []
    success_count = 0
    fail_count = 0
    
    for i, video in enumerate(video_data, 1):
        video_id = video['video_id']
        title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
        
        print(f"\n[{i:3d}/{total_videos}] 处理视频: {title}")
        print(f"Video ID: {video_id}")
        print(f"Published At: {video['published_at']}")
        
        # 发送请求
        result = request_srt_for_video(video_id, fetch_only=False)
        
        # 打印请求结果
        print(f"Request Result: {result}")
        
        # 记录结果
        result_record = {
            'index': i,
            'video_id': video_id,
            'title': video['title'],
            'published_at': video['published_at'],
            'request_result': result
        }
        results.append(result_record)
        
        if result['success']:
            success_count += 1
            print(f"✅ 成功")
        else:
            fail_count += 1
            print(f"❌ 失败: {result['error']}")
        
        # 显示进度
        progress = (i / total_videos) * 100
        print(f"📈 进度: {progress:.1f}% (成功:{success_count}, 失败:{fail_count})")
        
        # 延迟避免请求过于频繁
        if i < total_videos:  # 最后一个请求不需要延迟
            time.sleep(delay)
    
    # 保存结果
    timestamp = int(time.time())
    result_filename = f'srt_requests_results_{timestamp}.json'
    
    summary = {
        'timestamp': timestamp,
        'total_videos': total_videos,
        'success_count': success_count,
        'fail_count': fail_count,
        'success_rate': f"{(success_count/total_videos)*100:.1f}%",
        'results': results
    }
    
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 显示最终统计
    print("\n" + "=" * 50)
    print("🎯 批量请求完成!")
    print(f"📊 最终统计:")
    print(f"   - 总视频数: {total_videos}")
    print(f"   - 成功请求: {success_count}")
    print(f"   - 失败请求: {fail_count}")
    print(f"   - 成功率: {(success_count/total_videos)*100:.1f}%")
    print(f"💾 详细结果已保存到: {result_filename}")
    
    return results

def get_all_channel_videos():
    """获取频道的所有视频"""
    print("=== 获取完整频道数据 ===")
    
    # 从环境变量获取API密钥
    API_KEY = get_api_key()
    if not API_KEY:
        return
    
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    print(f"正在获取频道 {LIYONGLE_CHANNEL_ID} 的所有视频...")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    # 获取所有视频（不设置max_videos限制）
    video_data = fetcher.get_channel_videos(LIYONGLE_CHANNEL_ID)
    
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
        
        # 询问是否进行SRT字幕请求
        print(f"\n{'='*50}")
        srt_choice = input(f"是否要为所有 {len(video_data)} 个视频请求SRT字幕？\n1. 是，处理所有视频\n2. 是，但只处理前10个视频(测试)\n3. 是，但只处理前50个视频\n4. 否，跳过\n请选择 (1-4): ").strip()
        
        if srt_choice == '1':
            batch_request_srt(video_data)
        elif srt_choice == '2':
            batch_request_srt(video_data, max_requests=10)
        elif srt_choice == '3':
            batch_request_srt(video_data, max_requests=50)
        else:
            print("跳过SRT字幕请求")
            
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
    
    print(f"正在获取频道最近的 {count} 个视频...")
    video_data = fetcher.get_channel_videos(LIYONGLE_CHANNEL_ID, max_videos=count)
    
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
        
        # 询问是否进行SRT字幕请求
        srt_choice = input(f"\n是否要为这 {len(video_data)} 个视频请求SRT字幕？(y/n): ").strip().lower()
        if srt_choice in ['y', 'yes', '是']:
            batch_request_srt(video_data)
    else:
        print("❌ 未能获取到视频数据")

if __name__ == "__main__":
    print("YouTube频道完整数据获取工具 + SRT字幕请求")
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
