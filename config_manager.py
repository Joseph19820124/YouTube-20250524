import os
import json
from google.oauth2.service_account import Credentials

class ConfigManager:
    # GOOGLE_SHEETS_SCOPES from get_all_videos.py
    GOOGLE_SHEETS_SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]

    def __init__(self):
        self.youtube_api_key = self._load_api_key()
        self.google_credentials = self._load_google_credentials()

    def _load_api_key(self):
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

    def _load_google_credentials(self):
        """从环境变量或文件获取Google凭据"""
        # 方法1: 从环境变量获取服务账号JSON
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            try:
                service_account_info = json.loads(service_account_json)
                credentials = Credentials.from_service_account_info(
                    service_account_info, scopes=self.GOOGLE_SHEETS_SCOPES
                )
                return credentials
            except json.JSONDecodeError:
                print("❌ GOOGLE_SERVICE_ACCOUNT_JSON 格式错误")

        # 方法2: 从文件获取服务账号JSON
        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')
        if os.path.exists(service_account_file):
            try:
                credentials = Credentials.from_service_account_file(
                    service_account_file, scopes=self.GOOGLE_SHEETS_SCOPES
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

    def get_youtube_api_key(self):
        return self.youtube_api_key

    def get_google_creds(self):
        return self.google_credentials
