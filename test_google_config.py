#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google服务账号配置测试脚本
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials

def test_google_credentials():
    """测试Google服务账号配置"""
    print("🧪 测试Google服务账号配置...")
    
    # Google Sheets 权限范围
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    credentials = None
    
    # 方法1: 从环境变量获取JSON
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if service_account_json:
        try:
            service_account_info = json.loads(service_account_json)
            credentials = Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
            print("✅ 成功从环境变量 GOOGLE_SERVICE_ACCOUNT_JSON 获取凭据")
        except json.JSONDecodeError:
            print("❌ GOOGLE_SERVICE_ACCOUNT_JSON 格式错误")
        except Exception as e:
            print(f"❌ 从环境变量获取凭据失败: {e}")
    
    # 方法2: 从文件路径获取
    if not credentials:
        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')
        if os.path.exists(service_account_file):
            try:
                credentials = Credentials.from_service_account_file(
                    service_account_file, scopes=SCOPES
                )
                print(f"✅ 成功从文件 {service_account_file} 获取凭据")
            except Exception as e:
                print(f"❌ 从文件获取凭据失败: {e}")
        else:
            print(f"❌ 服务账号文件不存在: {service_account_file}")
    
    if not credentials:
        print("\n❌ 无法获取Google凭据，请检查配置:")
        print("1. 设置环境变量 GOOGLE_SERVICE_ACCOUNT_JSON")
        print("2. 或设置环境变量 GOOGLE_SERVICE_ACCOUNT_FILE")
        print("3. 或将service_account.json放在当前目录")
        return False
    
    # 测试连接
    try:
        gc = gspread.authorize(credentials)
        print("✅ Google Sheets连接测试成功")
        
        # 获取服务账号信息
        if hasattr(credentials, 'service_account_email'):
            print(f"📧 服务账号邮箱: {credentials.service_account_email}")
        
        print("\n✅ 配置测试完成！您可以开始使用多频道处理功能了。")
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets连接失败: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 检查是否已启用Google Sheets API和Google Drive API")
        print("2. 确认服务账号JSON文件格式正确")
        print("3. 检查网络连接")
        return False

def create_test_sheet_example():
    """创建测试用的Google Sheets示例"""
    print("\n📊 Google Sheets设置示例:")
    print("1. 创建新的Google Sheets")
    print("2. 在A列添加YouTube频道ID:")
    print("   A1: UCfq75-6J5seC82CmtLSFxXw")
    print("   A2: UCanFwnk3aOnfeRaYQfmWJ-g") 
    print("   A3: UC_x5XG1OV2P6uZZ5FSM9Ttw")
    print("3. 分享给服务账号邮箱，权限设为Viewer")
    print("4. 复制Sheets URL中的ID用于程序配置")

if __name__ == "__main__":
    print("🔧 Google服务账号配置测试工具")
    print("=" * 50)
    
    success = test_google_credentials()
    
    if not success:
        create_test_sheet_example()
    
    print("\n📖 更多帮助信息请查看README.md")
