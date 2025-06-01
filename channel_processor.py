import time
import json
import os # For path operations if needed

from youtube_video_fetcher import YouTubeVideoFetcher
from srt_service import SrtService

class ChannelProcessor:
    def __init__(self, fetcher: YouTubeVideoFetcher, srt_service: SrtService):
        self.fetcher = fetcher
        self.srt_service = srt_service

    def _get_channel_info(self, channel_id: str):
        """获取频道基本信息"""
        # This is a simplified version.
        # If more details are needed from YouTube API, self.fetcher could be used here.
        try:
            return {"id": channel_id, "name": f"Channel_{channel_id[:8]}"}
        except Exception:
            return {"id": channel_id, "name": f"Unknown_{channel_id[:8]}"}

    def process_channel(self, channel_id: str, max_videos: int = None, srt_mode: str = None):
        """处理单个频道的所有视频"""
        print(f"\n{'='*60}")
        print(f"🎯 开始处理频道: {channel_id}")
        print(f"{'='*60}")

        # 获取频道信息 using the internal helper method
        channel_info = self._get_channel_info(channel_id)

        print(f"正在获取频道 {channel_id} ({channel_info.get('name', '')}) 的视频...")
        if max_videos:
            print(f"限制获取最近 {max_videos} 个视频")
        else:
            print("获取所有视频（这可能需要较长时间）")
        print("请耐心等待...\n")

        # 获取视频数据 using self.fetcher
        try:
            if max_videos:
                video_data = self.fetcher.get_channel_videos(channel_id, max_videos=max_videos)
            else:
                video_data = self.fetcher.get_channel_videos(channel_id)
        except Exception as e:
            print(f"❌ 获取频道视频时出错: {e}")
            return None

        if not video_data:
            print(f"❌ 频道 {channel_id} 未能获取到视频数据")
            print("可能原因:")
            print("1. 频道ID不正确")
            print("2. 频道没有公开视频")
            print("3. YouTube API配额不足")
            print("4. 网络连接问题")
            return None

        print(f"\n🎉 成功获取 {len(video_data)} 个视频!")

        # 显示统计信息
        print(f"\n📊 统计信息:")
        print(f"- 频道ID: {channel_id}")
        print(f"- 总视频数量: {len(video_data)}")
        if video_data: # Ensure video_data is not empty before accessing elements
            print(f"- 最新视频: {video_data[0]['title']}")
            print(f"- 最早视频: {video_data[-1]['title']}")

        # 保存为不同格式
        safe_channel_name = channel_info['name'].replace(' ', '_').replace('/', '_').replace('\\', '_')
        timestamp = int(time.time())

        print(f"\n💾 保存文件...")
        try:
            # Use self.fetcher to save files
            self.fetcher.save_to_file(video_data, f'{safe_channel_name}_all_video_ids_{timestamp}.txt', 'txt')
            self.fetcher.save_to_file(video_data, f'{safe_channel_name}_all_videos_{timestamp}.json', 'json')
            self.fetcher.save_to_file(video_data, f'{safe_channel_name}_all_videos_{timestamp}.csv', 'csv')

            print("✅ 数据已保存为:")
            print(f"- {safe_channel_name}_all_video_ids_{timestamp}.txt (纯视频ID列表)")
            print(f"- {safe_channel_name}_all_videos_{timestamp}.json (完整JSON数据)")
            print(f"- {safe_channel_name}_all_videos_{timestamp}.csv (CSV表格格式)")
        except Exception as e:
            print(f"⚠️  保存文件时出错: {e}")

        # 显示前3个视频作为预览
        if video_data: # Ensure video_data is not empty
            print(f"\n🔍 最新3个视频预览:")
            for i, video in enumerate(video_data[:3], 1):
                print(f"{i}. {video['title']} ({video['published_at'][:10]})")

        # SRT字幕请求 using self.srt_service
        srt_results = []
        if srt_mode == 'all':
            srt_results = self.srt_service.batch_request_srt(video_data, channel_info)
        elif srt_mode == 'test':
            srt_results = self.srt_service.batch_request_srt(video_data, channel_info, max_requests=10)
        elif srt_mode == 'limited':
            srt_results = self.srt_service.batch_request_srt(video_data, channel_info, max_requests=50)
        elif srt_mode == 'ask':
            print(f"\n{'='*50}")
            srt_choice = input(f"是否要为频道 {channel_info['name']} 的 {len(video_data)} 个视频请求SRT字幕？\n1. 是，处理所有视频\n2. 是，但只处理前10个视频(测试)\n3. 是，但只处理前50个视频\n4. 否，跳过\n请选择 (1-4): ").strip()

            if srt_choice == '1':
                srt_results = self.srt_service.batch_request_srt(video_data, channel_info)
            elif srt_choice == '2':
                srt_results = self.srt_service.batch_request_srt(video_data, channel_info, max_requests=10)
            elif srt_choice == '3':
                srt_results = self.srt_service.batch_request_srt(video_data, channel_info, max_requests=50)
            else:
                print("跳过SRT字幕请求")

        # 保存SRT结果
        if srt_results:
            srt_filename = f'{safe_channel_name}_srt_results_{timestamp}.json'
            try:
                with open(srt_filename, 'w', encoding='utf-8') as f:
                    json.dump(srt_results, f, ensure_ascii=False, indent=2)
                print(f"💾 SRT请求结果已保存到: {srt_filename}")
            except Exception as e:
                print(f"⚠️  保存SRT结果时出错: {e}")

        return {
            'channel_info': channel_info,
            'video_data': video_data,
            'srt_results': srt_results
        }
