import time
import json
import sys # For sys.exit()

from config_manager import ConfigManager
from youtube_video_fetcher import YouTubeVideoFetcher
from srt_service import SrtService
from channel_processor import ChannelProcessor
from google_sheets_reader import GoogleSheetsReader

class App:
    def __init__(self):
        self.config_manager = ConfigManager()

        self.youtube_api_key = self.config_manager.get_youtube_api_key()
        # Initializing video_fetcher, srt_service, channel_processor, sheets_reader
        # with checks for youtube_api_key where necessary.

        if not self.youtube_api_key:
            print("🔴 CRITICAL: YouTube API Key not found. Please set YOUTUBE_API_KEY environment variable.")
            print("Modes requiring YouTube API access will not be available.")
            self.video_fetcher = None
            self.channel_processor = None
        else:
            self.video_fetcher = YouTubeVideoFetcher(self.youtube_api_key)
            # SrtService can be initialized even if API key is missing, as it doesn't take it directly.
            self.srt_service = SrtService()
            self.channel_processor = ChannelProcessor(self.video_fetcher, self.srt_service)

        # These can be initialized regardless of API key status, but their methods might fail or be limited.
        self.srt_service = SrtService() # Ensure it's initialized even if API key is missing for other uses
        if not hasattr(self, 'channel_processor'): # If API key was missing
            self.channel_processor = ChannelProcessor(self.video_fetcher, self.srt_service) if self.video_fetcher else None


        self.sheets_reader = GoogleSheetsReader(self.config_manager)

    def _show_usage_help(self):
        """显示使用帮助"""
        print("📖 使用帮助:")
        print("\n🔧 环境配置:")
        print("1. YouTube API密钥:")
        print("   export YOUTUBE_API_KEY='你的YouTube_API密钥'")
        print("\n2. Google服务账号配置 (多频道模式需要):")
        print("   方法A: export GOOGLE_SERVICE_ACCOUNT_JSON='完整JSON内容'")
        print("   方法B: export GOOGLE_SERVICE_ACCOUNT_FILE='/path/to/service_account.json'")
        print("   方法C: 将service_account.json放在当前目录")
        print("\n📊 Google Sheets格式:")
        print("- 在A列放置YouTube频道ID")
        print("- 每行一个频道ID")
        print("- 频道ID格式: UCxxxxxxxxxxxxxxxxxx (以UC开头，24个字符)")
        print("- 可选择是否包含标题行")
        print("\n🔗 获取频道ID方法:")
        print("1. 访问YouTube频道页面")
        print("2. 查看URL中的频道ID部分")
        print("3. 或使用浏览器开发者工具查看页面源码")

    def _run_single_channel_mode(self):
        """单频道处理模式"""
        if not self.youtube_api_key:
            print("🔴 YouTube API Key is not configured. Cannot run single channel mode.")
            return
        if not self.channel_processor:
            print("🔴 Channel Processor is not initialized. Cannot run single channel mode.")
            return

        print("=== 单频道处理模式 ===")

        channel_id = input("请输入YouTube频道ID: ").strip()
        if not channel_id:
            print("❌ 请提供有效的频道ID")
            return

        if len(channel_id) != 24 or not channel_id.startswith('UC'):
            print("⚠️  频道ID格式可能不正确，YouTube频道ID通常以'UC'开头，长度为24个字符")
            confirm = input("是否继续? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes', '是']:
                return

        choice = input("选择操作:\n1. 获取所有视频\n2. 获取最近50个视频\n3. 获取最近100个视频\n请输入选择 (1-3): ").strip()

        max_videos = None
        if choice == '2':
            max_videos = 50
        elif choice == '3':
            max_videos = 100

        # self.video_fetcher is already initialized in __init__
        # self.channel_processor is already initialized in __init__
        result = self.channel_processor.process_channel(channel_id, max_videos, 'ask')

        if result:
            print("\n🎉 操作完成!")
        else:
            print("\n❌ 操作失败!")

    def _run_multi_channel_mode(self):
        """从Google Sheets读取频道ID并批量处理"""
        if not self.youtube_api_key:
            print("🔴 YouTube API Key is not configured. Cannot run multi-channel mode.")
            return
        if not self.channel_processor or not self.sheets_reader:
            print("🔴 Critical components (Channel Processor or Sheets Reader) are not initialized. Cannot run multi-channel mode.")
            return

        print("=== 多频道批量处理模式 ===")
        print("📊 从Google Sheets读取YouTube频道ID列表，批量处理所有频道\n")

        print("📋 Google Sheets配置:")
        spreadsheet_id = input("请输入Google Sheets的ID (从URL中获取): ").strip()
        if not spreadsheet_id:
            print("❌ 请提供有效的Google Sheets ID")
            return

        sheet_name = input("请输入工作表名称 (默认: Sheet1): ").strip() or "Sheet1"
        column_range = input("请输入列范围 (默认: A:A): ").strip() or "A:A"

        channel_ids = self.sheets_reader.read_channel_ids(spreadsheet_id, sheet_name, column_range)
        if not channel_ids:
            return

        print(f"\n📋 共找到 {len(channel_ids)} 个有效频道")
        max_videos_choice = input("选择视频获取模式:\n1. 获取所有视频\n2. 获取最近50个视频\n3. 获取最近100个视频\n请选择 (1-3): ").strip()

        max_videos = None
        if max_videos_choice == '2':
            max_videos = 50
        elif max_videos_choice == '3':
            max_videos = 100

        srt_mode_choice = input("\n选择SRT字幕处理模式:\n1. 每个频道都询问\n2. 全部跳过\n3. 全部处理所有视频\n4. 全部只处理前10个视频(测试)\n5. 全部只处理前50个视频\n请选择 (1-5): ").strip()

        srt_mode_map = {'1': 'ask', '2': 'skip', '3': 'all', '4': 'test', '5': 'limited'}
        srt_mode = srt_mode_map.get(srt_mode_choice, 'ask')

        print(f"\n🚀 准备开始批量处理:")
        print(f"- 频道数量: {len(channel_ids)}")
        print(f"- 视频模式: {'所有视频' if not max_videos else f'最近{max_videos}个视频'}")
        print(f"- SRT模式: {srt_mode}")

        confirm = input("\n确认开始处理? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("操作已取消")
            return

        # self.video_fetcher, self.srt_service, self.channel_processor initialized in __init__

        all_results = []
        total_channels = len(channel_ids)
        failed_channels = []
        start_time = time.time()

        for i, channel_id_to_process in enumerate(channel_ids, 1):
            print(f"\n{'🚀' * 3} 正在处理频道 {i}/{total_channels}: {channel_id_to_process} {'🚀' * 3}")
            try:
                result = self.channel_processor.process_channel(channel_id_to_process, max_videos, srt_mode)
                if result:
                    all_results.append(result)
                    print(f"✅ 频道 {channel_id_to_process} 处理成功")
                else:
                    failed_channels.append(channel_id_to_process)
                    print(f"❌ 频道 {channel_id_to_process} 处理失败")

                if i < total_channels:
                    delay_seconds = 5
                    print(f"\n⏱️  等待{delay_seconds}秒后处理下一个频道...")
                    time.sleep(delay_seconds)
            except KeyboardInterrupt:
                print(f"\n⚠️  用户中断操作，已处理 {len(all_results)} 个频道")
                break
            except Exception as e:
                print(f"❌ 处理频道 {channel_id_to_process} 时出错: {e}")
                failed_channels.append(channel_id_to_process)
                continue

        end_time = time.time()
        processing_time = end_time - start_time

        if all_results or failed_channels:
            timestamp = int(time.time())
            summary_filename = f'multi_channel_summary_{timestamp}.json'
            summary = {
                'timestamp': timestamp,
                'processing_time_seconds': processing_time,
                'total_channels_found': total_channels,
                'total_channels_processed': len(all_results),
                'total_channels_failed': len(failed_channels),
                'failed_channels': failed_channels,
                'settings': {
                    'max_videos': max_videos,
                    'srt_mode': srt_mode,
                    'spreadsheet_id': spreadsheet_id,
                    'sheet_name': sheet_name,
                    'column_range': column_range
                },
                'channels': []
            }
            total_videos_globally = 0
            total_srt_requests_globally = 0
            for res_item in all_results:
                channel_summary = {
                    'channel_info': res_item['channel_info'],
                    'video_count': len(res_item['video_data']),
                    'srt_request_count': len(res_item['srt_results'])
                }
                summary['channels'].append(channel_summary)
                total_videos_globally += len(res_item['video_data'])
                total_srt_requests_globally += len(res_item['srt_results'])

            summary['total_videos'] = total_videos_globally
            summary['total_srt_requests'] = total_srt_requests_globally

            try:
                with open(summary_filename, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                print(f"\n💾 汇总报告已保存到: {summary_filename}")
            except Exception as e:
                print(f"⚠️  保存汇总报告时出错: {e}")

            print(f"\n{'='*60}")
            print("🎉 批量处理完成!")
            print(f"📊 最终统计:")
            print(f"   - 处理频道数: {len(all_results)}/{total_channels}")
            print(f"   - 成功频道数: {len(all_results)}")
            print(f"   - 失败频道数: {len(failed_channels)}")
            print(f"   - 总视频数: {total_videos_globally}")
            print(f"   - 总SRT请求数: {total_srt_requests_globally}")
            print(f"   - 处理时间: {processing_time/60:.1f} 分钟")
            if failed_channels:
                print(f"\n❌ 失败的频道:")
                for fc_id in failed_channels:
                    print(f"   - {fc_id}")
        else:
            print("\n❌ 没有成功处理任何频道")

    def run(self):
        print("🎬 YouTube频道完整数据获取工具 + SRT字幕请求")
        print("📊 支持单频道处理和多频道批量处理 (从Google Sheets读取)")
        print("🔑 使用环境变量获取API密钥和凭据\n")

        mode = input("选择处理模式:\n1. 单频道处理\n2. 多频道批量处理 (从Google Sheets读取)\n3. 显示使用帮助\n请选择 (1-3): ").strip()

        if mode == '1':
            if not self.youtube_api_key or not self.channel_processor:
                print("🔴 YouTube API Key is missing or Channel Processor could not be initialized. Cannot run single channel mode.")
                return
            self._run_single_channel_mode()
        elif mode == '2':
            if not self.youtube_api_key or not self.channel_processor or not self.sheets_reader:
                 print("🔴 YouTube API Key is missing or critical components could not be initialized. Cannot run multi-channel mode.")
                 return
            self._run_multi_channel_mode()
        elif mode == '3':
            self._show_usage_help()
        else:
            print("无效选择，请输入1, 2, 或 3。")

# if __name__ == '__main__':
#     # This is for testing app.py directly if ever needed,
#     # but get_all_videos.py will be the main entry point.
#     application = App()
#     application.run()
#     print("\n🎉 (app.py) 程序结束!")
