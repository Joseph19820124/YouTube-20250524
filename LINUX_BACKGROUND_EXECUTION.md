# Linux后台执行SRT批量下载脚本指南

在Linux系统上，有多种方式可以让脚本在后台运行，以下是几种推荐的方法：

## 🚀 方法1: 使用 nohup（推荐）

```bash
# 生成脚本
python3 generate_srt_scripts.py
chmod +x download_srt_batch.sh

# 后台运行，输出重定向到文件
nohup ./download_srt_batch.sh > srt_download.log 2>&1 &

# 查看进程ID
echo $!

# 查看实时日志
tail -f srt_download.log
```

**优点**: 即使SSH连接断开，脚本仍会继续运行

## 🔧 方法2: 使用 screen（适合长时间运行）

```bash
# 安装screen（如果未安装）
sudo apt update && sudo apt install screen

# 创建新的screen会话
screen -S srt_download

# 在screen中运行脚本
chmod +x download_srt_batch.sh
./download_srt_batch.sh

# 断开screen会话（脚本继续运行）
# 按 Ctrl+A，然后按 D

# 重新连接到screen会话
screen -r srt_download

# 查看所有screen会话
screen -ls
```

## ⚡ 方法3: 使用 tmux（现代化选择）

```bash
# 安装tmux（如果未安装）
sudo apt update && sudo apt install tmux

# 创建新的tmux会话
tmux new-session -d -s srt_download

# 在tmux中运行脚本
tmux send-keys -t srt_download 'chmod +x download_srt_batch.sh' Enter
tmux send-keys -t srt_download './download_srt_batch.sh' Enter

# 查看tmux会话
tmux list-sessions

# 连接到tmux会话
tmux attach-session -t srt_download
```

## 🕐 方法4: 使用 at 命令（定时执行）

```bash
# 安装at（如果未安装）
sudo apt update && sudo apt install at

# 立即在后台执行
echo "cd $(pwd) && chmod +x download_srt_batch.sh && ./download_srt_batch.sh" | at now

# 或者5分钟后执行
echo "cd $(pwd) && chmod +x download_srt_batch.sh && ./download_srt_batch.sh" | at now + 5 minutes

# 查看待执行的任务
atq

# 删除任务（如果需要）
atrm <job_number>
```

## 🏃 方法5: 简单的后台运行

```bash
# 最简单的后台运行方式
chmod +x download_srt_batch.sh
./download_srt_batch.sh &

# 查看后台进程
jobs

# 将进程置于前台
fg

# 将进程重新置于后台
bg
```

## 📊 监控和管理后台进程

### 查看运行状态
```bash
# 查看进程
ps aux | grep download_srt_batch

# 查看CPU和内存使用
top -p <进程ID>

# 实时查看日志
tail -f srt_download_*.log
```

### 停止后台进程
```bash
# 方法1: 使用进程ID
kill <进程ID>

# 方法2: 强制停止
kill -9 <进程ID>

# 方法3: 按名称停止
pkill -f download_srt_batch
```

## 🎯 推荐的完整流程

```bash
# 1. 生成脚本
python3 generate_srt_scripts.py

# 2. 使用nohup后台运行（推荐）
nohup ./download_srt_batch.sh > srt_download.log 2>&1 &

# 3. 记录进程ID
echo "脚本进程ID: $!" > srt_process.pid

# 4. 实时监控日志
tail -f srt_download.log

# 5. 查看进度（另开终端）
grep "进度:" srt_download.log | tail -10
```

## 🔍 进度监控脚本

创建一个简单的监控脚本：

```bash
# 创建监控脚本
cat > monitor_srt.sh << 'EOF'
#!/bin/bash
echo "SRT下载进度监控"
echo "=================="

while true; do
    if pgrep -f "download_srt_batch.sh" > /dev/null; then
        clear
        echo "🚀 脚本正在运行..."
        echo "📊 最新进度:"
        tail -5 srt_download.log | grep -E "(进度:|处理第|成功:|失败)"
        echo ""
        echo "⏰ $(date)"
        echo "按 Ctrl+C 停止监控"
    else
        echo "❌ 脚本已停止运行"
        break
    fi
    sleep 5
done
EOF

chmod +x monitor_srt.sh
./monitor_srt.sh
```

## 📝 日志管理

```bash
# 查看最新进度
grep "进度:" srt_download.log | tail -1

# 查看成功数量
grep "成功:" srt_download.log | wc -l

# 查看失败数量  
grep "失败:" srt_download.log | wc -l

# 查看完成情况
grep "处理完成" srt_download.log
```

## ⚠️ 注意事项

1. **网络稳定性**: 确保服务器网络连接稳定
2. **磁盘空间**: 确保有足够空间存储日志文件
3. **API限制**: 遵守API服务商的访问限制
4. **系统资源**: 监控CPU和内存使用情况

选择最适合你需求的方法。如果是简单的一次性运行，推荐使用 `nohup`。如果需要频繁监控和管理，推荐使用 `screen` 或 `tmux`。
