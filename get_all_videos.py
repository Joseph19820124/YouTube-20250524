#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取完整频道数据示例 - 支持多频道批量处理
从Google Sheets读取YouTube频道ID列表，批量处理所有频道
"""

import os
import requests
import json
import time
import gspread
from google.oauth2.service_account import Credentials
from youtube_video_fetcher import YouTubeVideoFetcher

# Google Sheets 配置
GOOGLE_SHEETS_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

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

def get_google_credentials():
    """从环境变量或文件获取Google凭据"""
    # 方法1: 从环境变量获取服务账号JSON
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if service_account_json:
        try:
            service_account_info = json.loads(service_account_json)
            credentials = Credentials.from_service_account_info(
                service_account_info, scopes=GOOGLE_SHEETS_SCOPES
            )
            return credentials
        except json.JSONDecodeError:
            print("❌ GOOGLE_SERVICE_ACCOUNT_JSON 格式错误")
    
    # 方法2: 从文件获取服务账号JSON
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')
    if os.path.exists(service_account_file):
        try:
            credentials = Credentials.from_service_account_file(
                service_account_file, scopes=GOOGLE_SHEETS_SCOPES
            )
            return credentials
        except Exception as e:
            print(f"❌ 读取服务账号文件失败: {e}")
    
    print("❌ 请设置Google凭据:")
    print("方法1: 设置环境变量 GOOGLE_SERVICE_ACCOUNT_JSON (完整JSON内容)")
    print("方法2: 将service_account.json文件放在当前目录")
    print("方法3: 设置环境变量 GOOGLE_SERVICE_ACCOUNT_FILE 指向JSON文件路径")
    print("\n📖 获取Google服务账号密钥的步骤:")
    print("1. 访问 https://console.cloud.google.com/")
    print("2. 创建或选择项目")
    print("3. 启用 Google Sheets API 和 Google Drive API")
    print("4. 创建服务账号 -> 下载JSON密钥文件")
    print("5. 在Google Sheets中给服务账号邮箱分享权限")
    return None

def read_channel_ids_from_sheets(spreadsheet_id, sheet_name="Sheet1", column_range="A:A"):
    """从Google Sheets读取YouTube频道ID列表"""
    try:
        credentials = get_google_credentials()
        if not credentials:
            return None
        
        gc = gspread.authorize(credentials)
        
        # 打开指定的电子表格
        print(f"📊 正在连接Google Sheets: {spreadsheet_id}")
        spreadsheet = gc.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # 读取指定列的数据
        print(f"📋 正在读取工作表 '{sheet_name}' 的 {column_range} 列...")
        values = worksheet.get(column_range)
        
        # 提取频道ID（过滤空值和标题行）
        channel_ids = []
        for i, row in enumerate(values):
            if row and row[0].strip():
                channel_id = row[0].strip()
                # 跳过可能的标题行
                if i == 0 and (channel_id.lower() in ['channel_id', 'channel id', 'youtube_channel_id', 'id']):
                    continue
                # 验证是否看起来像YouTube频道ID
                if len(channel_id) == 24 and channel_id.startswith('UC'):
                    channel_ids.append(channel_id)
                elif len(channel_id) > 0:
                    print(f"⚠️  跳过可能无效的频道ID: {channel_id}")
        
        print(f"✅ 成功读取到 {len(channel_ids)} 个有效频道ID")
        for i, channel_id in enumerate(channel_ids, 1):
            print(f"  {i}. {channel_id}")
        
        return channel_ids
        
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"❌ 找不到Google Sheets: {spreadsheet_id}")
        print("请检查:")
        print("1. Spreadsheet ID是否正确")
        print("2. 是否已将服务账号邮箱添加到Sheets的共享权限中")
        return None
    except gspread.exceptions.WorksheetNotFound:
        print(f"❌ 找不到工作表: {sheet_name}")
        return None
    except Exception as e:
        print(f"❌ 读取Google Sheets失败: {e}")
        return None

def get_channel_info(fetcher, channel_id):
    """获取频道基本信息"""
    try:
        # 这里可以扩展调用YouTube API获取频道详细信息
        return {"id": channel_id, "name": f"Channel_{channel_id[:8]}"}
    except:
        return {"id": channel_id, "name": f"Unknown_{channel_id[:8]}"}

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

def batch_request_srt(video_data, channel_info, max_requests=None, delay=1.0):
    """批量请求所有视频的SRT字幕"""
    if not video_data:
        print("❌ 没有视频数据")
        return []
    
    total_videos = len(video_data)
    if max_requests:
        total_videos = min(total_videos, max_requests)
        video_data = video_data[:max_requests]
    
    print(f"\n🚀 开始为频道 {channel_info['name']} 批量请求SRT字幕...")
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
            'channel_id': channel_info['id'],
            'channel_name': channel_info['name'],
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
        if i < total_videos:
            time.sleep(delay)
    
    print(f"\n✅ 频道 {channel_info['name']} SRT请求处理完成!")
    print(f"📊 统计: 成功 {success_count}, 失败 {fail_count}")
    
    return results

def process_single_channel(fetcher, channel_id, max_videos=None, srt_mode=None):
    """处理单个频道的所有视频"""
    print(f"\n{'='*60}")
    print(f"🎯 开始处理频道: {channel_id}")
    print(f"{'='*60}")
    
    # 获取频道信息
    channel_info = get_channel_info(fetcher, channel_id)
    
    print(f"正在获取频道 {channel_id} 的视频...")
    if max_videos:
        print(f"限制获取最近 {max_videos} 个视频")
    else:
        print("获取所有视频（这可能需要较长时间）")
    print("请耐心等待...\n")
    
    # 获取视频数据
    try:
        if max_videos:
            video_data = fetcher.get_channel_videos(channel_id, max_videos=max_videos)
        else:
            video_data = fetcher.get_channel_videos(channel_id)
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
    print(f"- 最新视频: {video_data[0]['title']}")
    print(f"- 最早视频: {video_data[-1]['title']}")
    
    # 保存为不同格式
    safe_channel_name = channel_info['name'].replace(' ', '_').replace('/', '_').replace('\\', '_')
    timestamp = int(time.time())
    
    print(f"\n💾 保存文件...")
    try:
        fetcher.save_to_file(video_data, f'{safe_channel_name}_all_video_ids_{timestamp}.txt', 'txt')
        fetcher.save_to_file(video_data, f'{safe_channel_name}_all_videos_{timestamp}.json', 'json')
        fetcher.save_to_file(video_data, f'{safe_channel_name}_all_videos_{timestamp}.csv', 'csv')
        
        print("✅ 数据已保存为:")
        print(f"- {safe_channel_name}_all_video_ids_{timestamp}.txt (纯视频ID列表)")
        print(f"- {safe_channel_name}_all_videos_{timestamp}.json (完整JSON数据)")
        print(f"- {safe_channel_name}_all_videos_{timestamp}.csv (CSV表格格式)")
    except Exception as e:
        print(f"⚠️  保存文件时出错: {e}")
    
    # 显示前3个视频作为预览
    print(f"\n🔍 最新3个视频预览:")
    for i, video in enumerate(video_data[:3], 1):
        print(f"{i}. {video['title']} ({video['published_at'][:10]})")
    
    # SRT字幕请求
    srt_results = []
    if srt_mode == 'all':
        srt_results = batch_request_srt(video_data, channel_info)
    elif srt_mode == 'test':
        srt_results = batch_request_srt(video_data, channel_info, max_requests=10)
    elif srt_mode == 'limited':
        srt_results = batch_request_srt(video_data, channel_info, max_requests=50)
    elif srt_mode == 'ask':
        print(f"\n{'='*50}")
        srt_choice = input(f"是否要为频道 {channel_info['name']} 的 {len(video_data)} 个视频请求SRT字幕？\n1. 是，处理所有视频\n2. 是，但只处理前10个视频(测试)\n3. 是，但只处理前50个视频\n4. 否，跳过\n请选择 (1-4): ").strip()
        
        if srt_choice == '1':
            srt_results = batch_request_srt(video_data, channel_info)
        elif srt_choice == '2':
            srt_results = batch_request_srt(video_data, channel_info, max_requests=10)
        elif srt_choice == '3':
            srt_results = batch_request_srt(video_data, channel_info, max_requests=50)
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

def process_multiple_channels_from_sheets():
    """从Google Sheets读取频道ID并批量处理"""
    print("=== 多频道批量处理模式 ===")
    print("📊 从Google Sheets读取YouTube频道ID列表，批量处理所有频道\n")
    
    # 获取API密钥
    API_KEY = get_api_key()
    if not API_KEY:
        return
    
    # 获取Google Sheets配置
    print("📋 Google Sheets配置:")
    spreadsheet_id = input("请输入Google Sheets的ID (从URL中获取): ").strip()
    if not spreadsheet_id:
        print("❌ 请提供有效的Google Sheets ID")
        return
    
    sheet_name = input("请输入工作表名称 (默认: Sheet1): ").strip() or "Sheet1"
    column_range = input("请输入列范围 (默认: A:A): ").strip() or "A:A"
    
    # 读取频道ID列表
    channel_ids = read_channel_ids_from_sheets(spreadsheet_id, sheet_name, column_range)
    if not channel_ids:
        return
    
    # 选择处理模式
    print(f"\n📋 共找到 {len(channel_ids)} 个有效频道")
    max_videos_choice = input("选择视频获取模式:\n1. 获取所有视频\n2. 获取最近50个视频\n3. 获取最近100个视频\n请选择 (1-3): ").strip()
    
    max_videos = None
    if max_videos_choice == '2':
        max_videos = 50
    elif max_videos_choice == '3':
        max_videos = 100
    
    # 选择SRT处理模式
    srt_mode_choice = input("\n选择SRT字幕处理模式:\n1. 每个频道都询问\n2. 全部跳过\n3. 全部处理所有视频\n4. 全部只处理前10个视频(测试)\n5. 全部只处理前50个视频\n请选择 (1-5): ").strip()
    
    srt_mode_map = {'1': 'ask', '2': 'skip', '3': 'all', '4': 'test', '5': 'limited'}
    srt_mode = srt_mode_map.get(srt_mode_choice, 'ask')
    
    # 确认开始处理
    print(f"\n🚀 准备开始批量处理:")
    print(f"- 频道数量: {len(channel_ids)}")
    print(f"- 视频模式: {'所有视频' if not max_videos else f'最近{max_videos}个视频'}")
    print(f"- SRT模式: {srt_mode}")
    
    confirm = input("\n确认开始处理? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("操作已取消")
        return
    
    # 初始化YouTube获取器
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    # 处理所有频道
    all_results = []
    total_channels = len(channel_ids)
    failed_channels = []
    
    start_time = time.time()
    
    for i, channel_id in enumerate(channel_ids, 1):
        print(f"\n{'🚀' * 3} 正在处理频道 {i}/{total_channels}: {channel_id} {'🚀' * 3}")
        
        try:
            result = process_single_channel(fetcher, channel_id, max_videos, srt_mode)
            if result:
                all_results.append(result)
                print(f"✅ 频道 {channel_id} 处理成功")
            else:
                failed_channels.append(channel_id)
                print(f"❌ 频道 {channel_id} 处理失败")
            
            # 频道间延迟，避免API限制
            if i < total_channels:
                delay_seconds = 5
                print(f"\n⏱️  等待{delay_seconds}秒后处理下一个频道...")
                time.sleep(delay_seconds)
                
        except KeyboardInterrupt:
            print(f"\n⚠️  用户中断操作，已处理 {len(all_results)} 个频道")
            break
        except Exception as e:
            print(f"❌ 处理频道 {channel_id} 时出错: {e}")
            failed_channels.append(channel_id)
            continue
    
    # 计算处理时间
    end_time = time.time()
    processing_time = end_time - start_time
    
    # 保存汇总结果
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
        
        total_videos = 0
        total_srt_requests = 0
        
        for result in all_results:
            channel_summary = {
                'channel_info': result['channel_info'],
                'video_count': len(result['video_data']),
                'srt_request_count': len(result['srt_results'])
            }
            summary['channels'].append(channel_summary)
            total_videos += len(result['video_data'])
            total_srt_requests += len(result['srt_results'])
        
        summary['total_videos'] = total_videos
        summary['total_srt_requests'] = total_srt_requests
        
        try:
            with open(summary_filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存汇总报告时出错: {e}")
        
        # 显示最终统计
        print(f"\n{'='*60}")
        print("🎉 批量处理完成!")
        print(f"📊 最终统计:")
        print(f"   - 处理频道数: {len(all_results)}/{total_channels}")
        print(f"   - 成功频道数: {len(all_results)}")
        print(f"   - 失败频道数: {len(failed_channels)}")
        print(f"   - 总视频数: {total_videos}")
        print(f"   - 总SRT请求数: {total_srt_requests}")
        print(f"   - 处理时间: {processing_time/60:.1f} 分钟")
        
        if failed_channels:
            print(f"\n❌ 失败的频道:")
            for channel_id in failed_channels:
                print(f"   - {channel_id}")
        
        print(f"\n💾 汇总报告已保存到: {summary_filename}")
    
    else:
        print("\n❌ 没有成功处理任何频道")

def process_single_channel_mode():
    """单频道处理模式"""
    print("=== 单频道处理模式 ===")
    
    # 获取API密钥
    API_KEY = get_api_key()
    if not API_KEY:
        return
    
    # 获取频道ID
    channel_id = input("请输入YouTube频道ID: ").strip()
    if not channel_id:
        print("❌ 请提供有效的频道ID")
        return
    
    # 验证频道ID格式
    if len(channel_id) != 24 or not channel_id.startswith('UC'):
        print("⚠️  频道ID格式可能不正确，YouTube频道ID通常以'UC'开头，长度为24个字符")
        confirm = input("是否继续? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            return
    
    # 选择处理模式
    choice = input("选择操作:\n1. 获取所有视频\n2. 获取最近50个视频\n3. 获取最近100个视频\n请输入选择 (1-3): ").strip()
    
    max_videos = None
    if choice == '2':
        max_videos = 50
    elif choice == '3':
        max_videos = 100
    
    # 初始化YouTube获取器
    fetcher = YouTubeVideoFetcher(API_KEY)
    
    # 处理频道
    result = process_single_channel(fetcher, channel_id, max_videos, 'ask')
    
    if result:
        print("\n🎉 操作完成!")
    else:
        print("\n❌ 操作失败!")

def show_usage_help():
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

if __name__ == "__main__":
    print("🎬 YouTube频道完整数据获取工具 + SRT字幕请求")
    print("📊 支持单频道处理和多频道批量处理 (从Google Sheets读取)")
    print("🔑 使用环境变量获取API密钥和凭据\n")
    
    mode = input("选择处理模式:\n1. 单频道处理\n2. 多频道批量处理 (从Google Sheets读取)\n3. 显示使用帮助\n请选择 (1-3): ").strip()
    
    if mode == '2':
        process_multiple_channels_from_sheets()
    elif mode == '3':
        show_usage_help()
    else:
        process_single_channel_mode()
    
    print("\n🎉 程序结束!")
