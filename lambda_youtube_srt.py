#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Lambda Function: 获取YouTube频道所有视频并请求SRT字幕
"""

import os
import json
import requests
import time
import logging
from youtube_video_fetcher import YouTubeVideoFetcher

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SRT API 配置
SRT_API_URL = 'https://lic.deepsrt.cc/webhook/get-srt-from-provider'

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
            return {
                "success": True, 
                "data": response.json(), 
                "status_code": response.status_code
            }
        else:
            return {
                "success": False, 
                "error": f"HTTP {response.status_code}", 
                "response": response.text
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求超时"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"请求异常: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"未知错误: {str(e)}"}

def lambda_handler(event, context):
    """
    AWS Lambda 主函数
    
    期望的输入格式:
    {
        "channel_id": "UCuDdJRJ6qR-wGILbpq-FXCw",
        "max_videos": null,  // 可选，限制处理的视频数量
        "delay": 1.0,        // 可选，请求间隔（秒）
        "fetch_only": false  // 可选，是否只获取而不处理
    }
    """
    
    try:
        # 解析输入参数
        channel_id = event.get('channel_id')
        max_videos = event.get('max_videos', None)
        delay = event.get('delay', 1.0)
        fetch_only = event.get('fetch_only', False)
        
        if not channel_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: channel_id'
                }, ensure_ascii=False)
            }
        
        # 从环境变量获取YouTube API密钥
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        if not youtube_api_key:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Missing YouTube API key in environment variables'
                }, ensure_ascii=False)
            }
        
        logger.info(f"开始处理频道: {channel_id}")
        
        # 初始化YouTube视频获取器
        fetcher = YouTubeVideoFetcher(youtube_api_key)
        
        # 获取频道的所有视频
        logger.info("正在获取频道视频...")
        video_data = fetcher.get_channel_videos(channel_id, max_videos=max_videos)
        
        if not video_data:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': f'No videos found for channel: {channel_id}'
                }, ensure_ascii=False)
            }
        
        total_videos = len(video_data)
        logger.info(f"成功获取 {total_videos} 个视频")
        
        # 批量请求SRT字幕
        results = []
        success_count = 0
        fail_count = 0
        
        logger.info("开始批量请求SRT字幕...")
        
        for i, video in enumerate(video_data, 1):
            video_id = video['video_id']
            title = video['title']
            
            logger.info(f"[{i}/{total_videos}] 处理视频: {video_id} - {title[:50]}")
            
            # 发送SRT请求
            srt_result = request_srt_for_video(video_id, fetch_only=fetch_only)
            
            # 记录结果
            result_record = {
                'index': i,
                'video_id': video_id,
                'title': title,
                'published_at': video['published_at'],
                'srt_request': srt_result
            }
            results.append(result_record)
            
            if srt_result['success']:
                success_count += 1
                logger.info(f"✅ 成功处理: {video_id}")
            else:
                fail_count += 1
                logger.warning(f"❌ 处理失败: {video_id} - {srt_result['error']}")
            
            # 添加延迟避免API限制
            if i < total_videos and delay > 0:
                time.sleep(delay)
        
        # 构造返回结果
        response_data = {
            'channel_id': channel_id,
            'total_videos': total_videos,
            'success_count': success_count,
            'fail_count': fail_count,
            'success_rate': f"{(success_count/total_videos)*100:.1f}%",
            'processing_time': context.get_remaining_time_in_millis() if context else 0,
            'results': results,
            'summary': {
                'latest_video': {
                    'title': video_data[0]['title'],
                    'video_id': video_data[0]['video_id'],
                    'published_at': video_data[0]['published_at']
                } if video_data else None,
                'oldest_video': {
                    'title': video_data[-1]['title'],
                    'video_id': video_data[-1]['video_id'],
                    'published_at': video_data[-1]['published_at']
                } if video_data else None
            }
        }
        
        logger.info(f"处理完成 - 成功: {success_count}, 失败: {fail_count}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            },
            'body': json.dumps(response_data, ensure_ascii=False, indent=2)
        }
        
    except Exception as e:
        logger.error(f"Lambda执行出错: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            }, ensure_ascii=False)
        }

# 本地测试函数
def test_locally():
    """本地测试函数"""
    # 模拟Lambda事件
    test_event = {
        "channel_id": "UCuDdJRJ6qR-wGILbpq-FXCw",  # 李永乐老师频道
        "max_videos": 5,  # 只处理前5个视频用于测试
        "delay": 0.5,
        "fetch_only": False
    }
    
    # 模拟Lambda上下文
    class MockContext:
        def get_remaining_time_in_millis(self):
            return 300000  # 5分钟
    
    # 确保设置了环境变量
    if not os.getenv('YOUTUBE_API_KEY'):
        print("❌ 请设置环境变量 YOUTUBE_API_KEY")
        return
    
    print("🧪 开始本地测试...")
    result = lambda_handler(test_event, MockContext())
    
    print(f"📊 测试结果:")
    print(f"状态码: {result['statusCode']}")
    print(f"响应体: {result['body']}")

if __name__ == "__main__":
    # 本地测试
    test_locally()
