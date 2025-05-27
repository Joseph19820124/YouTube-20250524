# YouTube多频道批量数据获取工具

这个工具支持从Google Sheets读取多个YouTube频道ID，并批量获取每个频道的视频数据和SRT字幕。

## 功能特点

- ✅ **单频道处理**: 处理单个YouTube频道
- ✅ **多频道批量处理**: 从Google Sheets读取频道列表，批量处理
- ✅ **灵活的视频获取**: 支持获取所有视频或限制数量
- ✅ **SRT字幕请求**: 为视频批量请求SRT字幕
- ✅ **多种输出格式**: TXT、JSON、CSV格式
- ✅ **详细的处理报告**: 包含成功/失败统计和汇总信息
- ✅ **错误处理**: 完善的错误处理和重试机制

## 环境配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置YouTube API密钥

```bash
# Linux/Mac
export YOUTUBE_API_KEY='你的YouTube_API密钥'

# Windows
set YOUTUBE_API_KEY=你的YouTube_API密钥

# PowerShell
$env:YOUTUBE_API_KEY='你的YouTube_API密钥'
```

### 3. 配置Google服务账号 (多频道模式需要)

有三种方法配置Google凭据：

#### 方法A: 环境变量 (推荐)
```bash
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...完整JSON内容...}'
```

#### 方法B: 文件路径
```bash
export GOOGLE_SERVICE_ACCOUNT_FILE='/path/to/service_account.json'
```

#### 方法C: 默认文件
将 `service_account.json` 文件放在项目根目录

## Google服务账号设置步骤

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建或选择项目
3. 启用以下API:
   - Google Sheets API
   - Google Drive API
4. 创建服务账号:
   - 转到 "IAM & Admin" > "Service Accounts"
   - 点击 "Create Service Account"
   - 下载JSON密钥文件
5. 共享Google Sheets:
   - 打开你的Google Sheets
   - 点击 "Share" 
   - 添加服务账号邮箱地址 (在JSON文件中的 `client_email`)
   - 给予 "Viewer" 权限

## Google Sheets格式

在Google Sheets中按以下格式准备数据：

| A列 (YouTube频道ID) |
|---------------------|
| UCfq75-6J5seC82CmtLSFxXw |
| UCanFwnk3aOnfeRaYQfmWJ-g |
| UC_x5XG1OV2P6uZZ5FSM9Ttw |

**注意事项:**
- 频道ID格式: `UCxxxxxxxxxxxxxxxxxx` (以UC开头，24个字符)
- 每行一个频道ID
- 可选择是否包含标题行 (程序会自动跳过)
- 确保频道ID有效且频道有公开视频

## 使用方法

### 运行程序
```bash
python get_all_videos.py
```

### 选择模式

程序会提示选择处理模式:

1. **单频道处理**: 手动输入单个频道ID进行处理
2. **多频道批量处理**: 从Google Sheets读取频道列表批量处理
3. **显示使用帮助**: 查看详细的使用说明

### 多频道处理流程

1. 输入Google Sheets ID (从URL获取)
2. 指定工作表名称 (默认: Sheet1)
3. 指定列范围 (默认: A:A)
4. 选择视频获取模式:
   - 获取所有视频
   - 获取最近50个视频
   - 获取最近100个视频
5. 选择SRT字幕处理模式:
   - 每个频道都询问
   - 全部跳过
   - 全部处理所有视频
   - 全部只处理前10个视频(测试)
   - 全部只处理前50个视频

## 输出文件

### 每个频道的输出文件:
- `{频道名}_all_video_ids_{时间戳}.txt` - 纯视频ID列表
- `{频道名}_all_videos_{时间戳}.json` - 完整视频数据
- `{频道名}_all_videos_{时间戳}.csv` - CSV格式数据
- `{频道名}_srt_results_{时间戳}.json` - SRT请求结果 (如果启用)

### 汇总报告:
- `multi_channel_summary_{时间戳}.json` - 包含所有频道的处理统计

## 示例配置

### 环境变量示例 (.env文件)
```env
YOUTUBE_API_KEY=AIzaSyA...your_api_key_here
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project",...}
```

### Google Sheets URL示例
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
```
Sheets ID 就是: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

## 错误排除

### 常见问题

1. **YouTube API配额不足**
   - 检查Google Cloud Console中的API配额
   - 考虑申请更高的配额或分批处理

2. **Google Sheets访问失败**
   - 确认服务账号邮箱已添加到Sheets共享列表
   - 检查Sheets ID是否正确
   - 确认Google Sheets API已启用

3. **频道ID无效**
   - 确认频道ID格式: 以UC开头，24个字符
   - 检查频道是否存在且有公开视频

4. **网络连接问题**
   - 检查网络连接
   - 考虑增加请求间隔时间

### 调试技巧

- 使用单频道模式测试单个频道ID
- 先用测试模式 (前10个视频) 验证配置
- 检查控制台输出的详细错误信息

## 注意事项

1. **API限制**: YouTube API有每日配额限制，大量频道处理时注意配额使用
2. **处理时间**: 获取所有视频可能需要较长时间，建议先测试少量频道
3. **存储空间**: 大量频道的数据文件可能占用较多磁盘空间
4. **网络稳定性**: 建议在网络稳定的环境下运行
5. **频道权限**: 只能获取公开视频，私有视频无法访问

## 技术规格

- Python 3.7+
- 依赖库: requests, gspread, google-auth
- 支持的输出格式: TXT, JSON, CSV
- 并发处理: 顺序处理 (避免API限制)
- 错误重试: 自动处理网络临时故障

## 更新日志

### v2.0 (当前版本)
- ✅ 新增多频道批量处理功能
- ✅ 集成Google Sheets读取功能
- ✅ 改进错误处理和用户体验
- ✅ 添加详细的处理报告
- ✅ 支持频道处理统计和失败重试

### v1.0
- ✅ 基础单频道视频获取功能
- ✅ SRT字幕请求功能
- ✅ 多种输出格式支持

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 许可证

本项目采用MIT许可证。
