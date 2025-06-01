import gspread
from config_manager import ConfigManager # Proper import for ConfigManager

class GoogleSheetsReader:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def read_channel_ids(self, spreadsheet_id: str, sheet_name: str = "Sheet1", column_range: str = "A:A"):
        """从Google Sheets读取YouTube频道ID列表"""
        try:
            # Use credentials from ConfigManager
            credentials = self.config_manager.get_google_creds()
            if not credentials:
                # The ConfigManager already prints detailed error messages.
                # We might add a specific message here if needed, or rely on ConfigManager's output.
                print("❌ Google Sheets credentials not available via ConfigManager.")
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
                if row and row[0].strip(): # Check if row is not empty and first cell is not empty
                    channel_id = row[0].strip()
                    # 跳过可能的标题行
                    if i == 0 and (channel_id.lower() in ['channel_id', 'channel id', 'youtube_channel_id', 'id']):
                        continue
                    # 验证是否看起来像YouTube频道ID
                    if len(channel_id) == 24 and channel_id.startswith('UC'):
                        channel_ids.append(channel_id)
                    elif len(channel_id) > 0: # Avoid printing warnings for completely empty trailing rows
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
