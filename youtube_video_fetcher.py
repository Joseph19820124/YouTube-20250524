#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube频道视频ID获取工具
使用YouTube Data API v3获取指定频道的所有视频ID
"""

import time
import json
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeVideoFetcher:
    def __init__(self, api_key: str):
        """
        初始化YouTube API客户端
        
        Args:
            api_key: YouTube Data API v3的API密钥
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def get_channel_uploads_playlist_id(self, channel_id: str) -> Optional[str]:
        """
        通过频道ID获取uploads播放列表ID
        
        Args:
            channel_id: YouTube频道ID
            
        Returns:
            uploads播放列表ID，如果失败返回None
        """
        try:
            # 方法1: 直接替换频道ID的第二个字符
            if channel_id.startswith('UC'):
                uploads_playlist_id = 'UU' + channel_id[2:]
                return uploads_playlist_id
            
            # 方法2: 通过API获取（更可靠）
            request = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            response = request.execute()
            
            if response['items']:
                uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                return uploads_playlist_id
            else:
                print(f"未找到频道ID: {channel_id}")
                return None
                
        except HttpError as e:
            print(f"获取频道信息时出错: {e}")
            return None
    
    def get_all_video_ids(self, playlist_id: str, max_videos: Optional[int] = None) -> List[str]:
        """
        获取播放列表中的所有视频ID
        
        Args:
            playlist_id: 播放列表ID
            max_videos: 最大获取视频数量，None表示获取所有
            
        Returns:
            视频ID列表
        """
        all_video_ids = []
        next_page_token = None
        request_count = 0
        
        print(f"开始获取播放列表 {playlist_id} 的视频...")
        
        while True:
            try:
                request = self.youtube.playlistItems().list(
                    part='contentDetails,snippet',  # 获取更多信息
                    playlistId=playlist_id,
                    maxResults=50,  # API允许的最大值
                    pageToken=next_page_token
                )
                response = request.execute()
                request_count += 1
                
                # 处理当前页的视频
                for item in response['items']:
                    video_id = item['contentDetails']['videoId']
                    video_title = item['snippet']['title']
                    publish_time = item['snippet']['publishedAt']
                    
                    all_video_ids.append({
                        'video_id': video_id,
                        'title': video_title,
                        'published_at': publish_time
                    })
                    
                    # 如果设置了最大数量限制
                    if max_videos and len(all_video_ids) >= max_videos:
                        print(f"已达到最大视频数量限制: {max_videos}")
                        return all_video_ids
                
                print(f"已获取 {len(all_video_ids)} 个视频 (第 {request_count} 次请求)")
                
                # 检查是否还有下一页
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # 添加延迟以避免触发API限制
                time.sleep(0.1)
                
            except HttpError as e:
                print(f"API请求出错: {e}")
                if e.resp.status == 403:
                    print("可能是API配额超限，请检查你的API密钥和配额设置")
                break
            except Exception as e:
                print(f"未知错误: {e}")
                break
        
        print(f"总共获取了 {len(all_video_ids)} 个视频，使用了 {request_count} 次API请求")
        return all_video_ids
    
    def get_channel_videos(self, channel_id: str, max_videos: Optional[int] = None) -> List[str]:
        """
        获取指定频道的所有视频ID
        
        Args:
            channel_id: YouTube频道ID
            max_videos: 最大获取视频数量
            
        Returns:
            视频信息列表
        """
        # 获取uploads播放列表ID
        uploads_playlist_id = self.get_channel_uploads_playlist_id(channel_id)
        if not uploads_playlist_id:
            return []
        
        print(f"频道 {channel_id} 的uploads播放列表ID: {uploads_playlist_id}")
        
        # 获取所有视频ID
        return self.get_all_video_ids(uploads_playlist_id, max_videos)
    
    def save_to_file(self, video_data: List[dict], filename: str, format_type: str = 'txt'):
        """
        将视频数据保存到文件
        
        Args:
            video_data: 视频数据列表
            filename: 文件名
            format_type: 文件格式 ('txt', 'json', 'csv')
        """
        try:
            if format_type == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    for video in video_data:
                        f.write(video['video_id'] + '\n')
            
            elif format_type == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(video_data, f, ensure_ascii=False, indent=2)
            
            elif format_type == 'csv':
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['video_id', 'title', 'published_at'])
                    writer.writeheader()
                    writer.writerows(video_data)
            
            print(f"数据已保存到 {filename}")
            
        except Exception as e:
            print(f"保存文件时出错: {e}")


def main():
    """主函数示例"""
    # 配置信息
    API_KEY = 'YOUR_API_KEY'  # 替换为你的API密钥
    CHANNEL_ID = 'UCMUnInmOkrWN4gof9KlhNmQ'  # 李永乐老师的频道ID
    
    # 创建获取器实例
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    # 获取频道的所有视频
    print("开始获取李永乐老师频道的所有视频...")
    video_data = fetcher.get_channel_videos(CHANNEL_ID)
    
    if video_data:
        print(f"\n成功获取 {len(video_data)} 个视频!")
        
        # 显示前5个视频的信息
        print("\n前5个视频:")
        for i, video in enumerate(video_data[:5]):
            print(f"{i+1}. {video['title']}")
            print(f"   ID: {video['video_id']}")
            print(f"   发布时间: {video['published_at']}")
            print()
        
        # 保存到不同格式的文件
        fetcher.save_to_file(video_data, 'liyongle_video_ids.txt', 'txt')
        fetcher.save_to_file(video_data, 'liyongle_videos.json', 'json')
        fetcher.save_to_file(video_data, 'liyongle_videos.csv', 'csv')
        
    else:
        print("未能获取到视频数据")


if __name__ == "__main__":
    main()
