# SRT批量下载脚本使用说明

本目录包含了用于批量下载YouTube视频SRT字幕的脚本和工具。

## 📁 文件说明

### 核心文件
- **`video_ids.txt`** - 包含358个YouTube视频ID的列表
- **`generate_srt_scripts.py`** - 脚本生成器，将视频ID转换为批量curl命令

### 生成的脚本文件
运行 `generate_srt_scripts.py` 后会生成以下三个脚本：
- **`download_srt_batch.sh`** - Linux/Mac Bash脚本
- **`download_srt_batch.bat`** - Windows批处理脚本  
- **`download_srt_batch.ps1`** - PowerShell脚本

## 🚀 快速开始

### 步骤1: 生成批量下载脚本

```bash
# 确保在仓库根目录下
python generate_srt_scripts.py
```

这会根据 `video_ids.txt` 生成三个平台的批量下载脚本。

### 步骤2: 运行相应平台的脚本

**Linux/Mac:**
```bash
chmod +x download_srt_batch.sh
./download_srt_batch.sh
```

**Windows:**
```cmd
download_srt_batch.bat
```

**PowerShell:**
```powershell
PowerShell -ExecutionPolicy Bypass -File download_srt_batch.ps1
```

## 📋 脚本功能特性

### ✨ 智能功能
- **进度显示** - 实时显示处理进度 (如: [156/358])
- **状态检查** - 自动检查HTTP响应状态
- **错误处理** - 记录成功/失败的请求
- **日志记录** - 所有操作自动保存到日志文件
- **统计报告** - 完成后显示成功率统计

### 🛡️ 安全特性
- **请求延迟** - 每个请求间隔1秒避免被限制
- **超时处理** - 避免无限等待
- **错误恢复** - 单个失败不影响整体进程

## 📊 输出示例

```
🚀 开始处理 358 个YouTube视频的SRT...
=======================================

📝 日志文件: srt_download_20250525_080315.log

[1/358] 处理视频: JCwi1U3PHIQ
🔗 YouTube链接: https://www.youtube.com/watch?v=JCwi1U3PHIQ
✅ 成功: {"status": "success", "message": "SRT fetch initiated"}
进度: 1 成功, 0 失败
---

[2/358] 处理视频: 5FEqfB-KRmY
🔗 YouTube链接: https://www.youtube.com/watch?v=5FEqfB-KRmY
✅ 成功: {"status": "success", "message": "SRT fetch initiated"}
进度: 2 成功, 0 失败
---
...

=======================================
🎉 处理完成！
📊 统计结果:
   总数: 358
   成功: 355
   失败: 3
   成功率: 99%

📝 详细日志已保存到: srt_download_20250525_080315.log
```

## 🔧 自定义配置

### 修改请求延迟
在生成的脚本中找到 `sleep 1` 并修改数值：
```bash
sleep 2  # 增加到2秒延迟
```

### 修改API端点
编辑 `generate_srt_scripts.py` 中的URL：
```python
# 当前API端点
https://lic.deepsrt.cc/webhook/get-srt-from-provider

# 可以修改为其他端点
```

### 添加更多视频ID
在 `video_ids.txt` 文件末尾添加新的视频ID，每行一个。

## 📝 日志文件说明

每次运行脚本都会生成带时间戳的日志文件：
- **格式**: `srt_download_YYYYMMDD_HHMMSS.log`
- **内容**: 每个视频的处理结果和响应信息
- **用途**: 调试错误、统计分析、重新处理失败项

## ⚠️ 注意事项

### API限制
- 请遵守API服务商的使用条款
- 避免过于频繁的请求
- 建议在非高峰期运行

### 网络要求
- 确保网络连接稳定
- 某些地区可能需要代理
- 建议在带宽充足的环境下运行

### 错误处理
- 网络超时: 脚本会自动重试
- API错误: 检查日志文件获取详细信息
- 权限问题: 确保脚本有执行权限

## 🛠️ 故障排除

### 常见问题

**Q: 脚本无法执行**
```bash
# Linux/Mac权限问题
chmod +x download_srt_batch.sh

# Windows PowerShell执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Q: curl命令未找到**
```bash
# Ubuntu/Debian
sudo apt install curl

# CentOS/RHEL
sudo yum install curl

# macOS
brew install curl

# Windows
# 使用Windows 10/11内置curl或下载curl
```

**Q: 大量请求失败**
- 检查网络连接
- 验证API端点是否可用
- 增加请求间隔时间

## 📈 批量处理建议

### 分批处理
对于大量视频，建议分批处理：
```bash
# 处理前100个视频
head -100 video_ids.txt > batch1.txt

# 处理101-200个视频  
sed -n '101,200p' video_ids.txt > batch2.txt
```

### 并行处理
**谨慎使用** - 可能触发API限制：
```bash
# GNU parallel (如果已安装)
cat video_ids.txt | parallel -j 5 curl -s -X POST https://lic.deepsrt.cc/webhook/get-srt-from-provider -H "Content-Type: application/json" -d '{"youtube_id":"{}", "fetch_only": "true"}'
```

## 🔗 相关链接

- **GitHub仓库**: [YouTube-20250524](https://github.com/Joseph19820124/YouTube-20250524)
- **API文档**: 请咨询API提供商
- **问题反馈**: 在GitHub Issues中提交

---

🎯 **目标**: 高效批量处理358个YouTube视频的SRT字幕获取  
⏱️ **预估时间**: 约6-10分钟（包含1秒延迟）  
🔄 **可重复**: 支持断点续传和重新处理失败项
