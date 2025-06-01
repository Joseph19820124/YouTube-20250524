import requests
import time
import json

class SrtService:
    SRT_API_URL = 'https://lic.deepsrt.cc/webhook/get-srt-from-provider'

    def __init__(self):
        pass

    def request_srt_for_video(self, video_id: str, fetch_only: bool = False):
        """为单个视频请求SRT字幕"""
        try:
            payload = {
                "youtube_id": video_id,
                "fetch_only": str(fetch_only).lower()
            }

            headers = {
                'Content-Type': 'application/json'
            }

            # Use the class attribute for the API URL
            response = requests.post(self.SRT_API_URL, headers=headers, json=payload, timeout=30)

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

    def batch_request_srt(self, video_data: list, channel_info: dict, max_requests: int = None, delay: float = 1.0):
        """批量请求所有视频的SRT字幕"""
        if not video_data:
            print("❌ 没有视频数据")
            return []

        total_videos = len(video_data)
        if max_requests:
            total_videos = min(total_videos, max_requests)
            video_data_to_process = video_data[:max_requests]
        else:
            video_data_to_process = video_data

        print(f"\n🚀 开始为频道 {channel_info['name']} 批量请求SRT字幕...")
        print(f"📊 总共需要处理 {len(video_data_to_process)} 个视频 (总视频数: {total_videos})")
        if max_requests:
            print(f"ℹ️  限制处理最近 {max_requests} 个视频")
        print(f"⏱️  请求间隔: {delay} 秒")
        print("=" * 50)

        results = []
        success_count = 0
        fail_count = 0

        for i, video in enumerate(video_data_to_process, 1):
            video_id = video['video_id']
            title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']

            print(f"\n[{i:3d}/{len(video_data_to_process)}] 处理视频: {title}")
            print(f"Video ID: {video_id}")
            print(f"Published At: {video['published_at']}")

            # 发送请求 using the class method
            result = self.request_srt_for_video(video_id, fetch_only=False)

            # 打印请求结果
            print(f"Request Result: {result}")

            # 记录结果
            result_record = {
                'channel_id': channel_info['id'],
                'channel_name': channel_info['name'],
                'index': i, # Index within the processed batch
                'original_index': video_data.index(video), # Index in the original list, if needed
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
            progress = (i / len(video_data_to_process)) * 100
            print(f"📈 进度: {progress:.1f}% (成功:{success_count}, 失败:{fail_count})")

            # 延迟避免请求过于频繁
            if i < len(video_data_to_process):
                time.sleep(delay)

        print(f"\n✅ 频道 {channel_info['name']} SRT请求处理完成!")
        print(f"📊 统计: 成功 {success_count}, 失败 {fail_count} (共处理 {len(video_data_to_process)} 个视频)")

        return results
