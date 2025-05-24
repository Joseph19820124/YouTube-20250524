# YouTube频道视频ID获取工具

这是一个使用YouTube Data API v3获取指定YouTube频道所有视频信息的Python工具。

## 功能特性

- 🎯 **精确获取**: 通过官方API获取频道的所有公开视频
- 📊 **多格式输出**: 支持TXT、JSON、CSV三种格式保存
- 🔄 **自动分页**: 自动处理API分页，获取所有视频
- 📈 **进度监控**: 实时显示获取进度和API使用情况
- 🛡️ **错误处理**: 完善的异常处理和API限制保护
- 📝 **详细信息**: 获取视频ID、标题、发布时间等信息
- 🔑 **环境变量**: 使用环境变量安全管理API密钥

## 安装依赖

```bash
pip install google-api-python-client
```

## API密钥设置

### 1. 创建Google Cloud项目
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目

### 2. 启用YouTube Data API v3
1. 在项目中搜索"YouTube Data API v3"
2. 点击启用API

### 3. 创建API密钥
1. 转到"凭据"页面
2. 点击"创建凭据" > "API密钥"
3. 复制生成的API密钥

### 4. 设置环境变量（推荐方式）

**Linux/Mac:**
```bash
export YOUTUBE_API_KEY='你的API密钥'
```

**Windows 命令提示符:**
```cmd
set YOUTUBE_API_KEY=你的API密钥
```

**Windows PowerShell:**
```powershell
$env:YOUTUBE_API_KEY='你的API密钥'
```

**持久化设置（推荐）:**
```bash
# Linux/Mac - 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export YOUTUBE_API_KEY="你的API密钥"' >> ~/.bashrc
source ~/.bashrc

# Windows - 通过系统设置添加环境变量
# 控制面板 > 系统 > 高级系统设置 > 环境变量
```

## 使用方法

### 基础使用

```python
from youtube_video_fetcher import YouTubeVideoFetcher

# 现在自动从环境变量获取API密钥
fetcher = YouTubeVideoFetcher(os.getenv('YOUTUBE_API_KEY'))

# 获取李永乐老师频道的所有视频
channel_id = 'UCMUnInmOkrWN4gof9KlhNmQ'
video_data = fetcher.get_channel_videos(channel_id)

# 保存到文件
fetcher.save_to_file(video_data, 'videos.json', 'json')
```

### 快速开始

**1. 运行示例脚本:**
```bash
python example.py
```

**2. 获取所有视频:**
```bash
python get_all_videos.py
```

**3. 交互式测试:**
```bash
python my_test.py
```

### 限制获取数量

```python
# 只获取前100个视频
video_data = fetcher.get_channel_videos(channel_id, max_videos=100)
```

### 不同保存格式

```python
# 保存为纯文本（仅视频ID）
fetcher.save_to_file(video_data, 'video_ids.txt', 'txt')

# 保存为JSON（完整信息）
fetcher.save_to_file(video_data, 'videos.json', 'json')

# 保存为CSV（表格格式）
fetcher.save_to_file(video_data, 'videos.csv', 'csv')
```

## 输出格式说明

### TXT格式
```
dQw4w9WgXcQ
kJQP7kiw5Fk
9bZkp7q19f0
...
```

### JSON格式
```json
[
  {
    "video_id": "dQw4w9WgXcQ",
    "title": "视频标题",
    "published_at": "2023-01-01T00:00:00Z"
  },
  ...
]
```

### CSV格式
```csv
video_id,title,published_at
dQw4w9WgXcQ,视频标题,2023-01-01T00:00:00Z
...
```

## 频道ID获取方法

### 方法1: 从频道URL获取
- 频道URL: `https://www.youtube.com/channel/UCMUnInmOkrWN4gof9KlhNmQ`
- 频道ID: `UCMUnInmOkrWN4gof9KlhNmQ`

### 方法2: 从自定义URL获取
1. 打开频道页面
2. 查看页面源代码
3. 搜索 `"channelId"` 或 `"externalId"`

## API配额说明

- **免费配额**: 每日10,000单位
- **每次请求**: 约1单位
- **561个视频**: 约需12次请求（远低于限制）

## 示例频道

本工具以李永乐老师的YouTube频道为示例：
- **频道名**: 李永乐老师官方
- **频道ID**: UCMUnInmOkrWN4gof9KlhNmQ
- **视频数量**: 约561个

## 文件说明

| 文件 | 用途 | 特点 |
|------|------|------|
| `youtube_video_fetcher.py` | 主工具类 | 核心功能，可单独使用 |
| `example.py` | 基础示例 | 演示多种用法，限制获取数量 |
| `get_all_videos.py` | 完整数据获取 | 可获取频道所有视频 |
| `my_test.py` | 交互式测试 | 菜单式选择功能 |

## 环境变量优势

✅ **安全性**: API密钥不会意外提交到代码仓库  
✅ **便利性**: 只需设置一次，所有脚本自动获取  
✅ **标准化**: 符合12-Factor App原则  
✅ **灵活性**: 不同环境可使用不同密钥  

## 注意事项

1. **API密钥安全**: 使用环境变量，避免硬编码到代码中
2. **配额限制**: 注意API的每日配额限制
3. **请求频率**: 工具已内置延迟以避免触发限制
4. **私有视频**: 只能获取公开的视频

## 错误处理

工具包含完善的错误处理机制：
- 环境变量检查和提示
- API配额超限提醒
- 网络错误重试建议
- 频道不存在的提示
- 文件保存错误处理

## 快速排错

**问题**: `❌ 请设置环境变量 YOUTUBE_API_KEY`
```bash
# 解决方法
export YOUTUBE_API_KEY='你的API密钥'
```

**问题**: API请求出错
```bash
# 检查API密钥是否正确
echo $YOUTUBE_API_KEY

# 检查API配额是否充足
```

## 技术细节

### uploads播放列表ID转换
```python
# 方法1: 字符串替换
if channel_id.startswith('UC'):
    uploads_playlist_id = 'UU' + channel_id[2:]

# 方法2: API查询（更可靠）
response = youtube.channels().list(
    part='contentDetails',
    id=channel_id
).execute()
```

### 环境变量获取
```python
import os

def get_api_key():
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ 请设置环境变量 YOUTUBE_API_KEY")
        return None
    return api_key
```

### 分页处理
```python
while True:
    response = youtube.playlistItems().list(
        part='contentDetails,snippet',
        playlistId=playlist_id,
        maxResults=50,
        pageToken=next_page_token
    ).execute()
    
    # 处理当前页数据
    
    next_page_token = response.get('nextPageToken')
    if not next_page_token:
        break
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
