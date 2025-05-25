#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT批量下载脚本生成器
根据video_ids.txt生成批量curl命令脚本
"""

import os

def generate_curl_scripts():
    """生成curl命令脚本"""
    
    # 读取视频ID列表
    try:
        with open('video_ids.txt', 'r', encoding='utf-8') as f:
            video_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ 未找到 video_ids.txt 文件")
        print("请确保 video_ids.txt 文件在当前目录下")
        return
    
    print(f"📖 读取了 {len(video_ids)} 个视频ID")
    
    # 生成Bash脚本
    bash_script = generate_bash_script(video_ids)
    
    # 生成Windows批处理脚本
    windows_script = generate_windows_script(video_ids)
    
    # 生成PowerShell脚本
    powershell_script = generate_powershell_script(video_ids)
    
    # 保存脚本文件
    save_scripts(bash_script, windows_script, powershell_script, len(video_ids))

def generate_bash_script(video_ids):
    """生成Bash脚本"""
    script = f"""#!/bin/bash
# YouTube SRT批量获取脚本 (Bash版本)
# 总共 {len(video_ids)} 个视频
# 生成时间: $(date)

echo "🚀 开始处理 {len(video_ids)} 个YouTube视频的SRT..."
echo "======================================="
echo ""

# 创建日志文件
log_file="srt_download_$(date +%Y%m%d_%H%M%S).log"
echo "📝 日志文件: $log_file"
echo ""

# 计数器
success_count=0
error_count=0
total_count={len(video_ids)}

"""

    for index, video_id in enumerate(video_ids, 1):
        num = str(index).zfill(3)
        script += f"""
# {num}. 视频ID: {video_id}
echo "[{index}/{len(video_ids)}] 处理视频: {video_id}"
echo "🔗 YouTube链接: https://www.youtube.com/watch?v={video_id}"

# 执行curl命令
response=$(curl -s -X POST https://lic.deepsrt.cc/webhook/get-srt-from-provider \\
    -H "Content-Type: application/json" \\
    -d '{{"youtube_id":"{video_id}", "fetch_only": "true"}}' \\
    -w "\\n%{{http_code}}")

# 检查响应状态
http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    echo "✅ 成功: $response_body" | tee -a "$log_file"
    ((success_count++))
else
    echo "❌ 失败 (HTTP $http_code): $response_body" | tee -a "$log_file"
    ((error_count++))
fi

echo "进度: $success_count 成功, $error_count 失败"
echo "---"
sleep 1  # 避免请求过于频繁

"""

    script += f"""
echo "======================================="
echo "🎉 处理完成！"
echo "📊 统计结果:"
echo "   总数: $total_count"
echo "   成功: $success_count"
echo "   失败: $error_count"
echo "   成功率: $(( success_count * 100 / total_count ))%"
echo ""
echo "📝 详细日志已保存到: $log_file"
"""

    return script

def generate_windows_script(video_ids):
    """生成Windows批处理脚本"""
    script = f"""@echo off
chcp 65001 >nul
REM YouTube SRT批量获取脚本 (Windows版本)
REM 总共 {len(video_ids)} 个视频

echo 🚀 开始处理 {len(video_ids)} 个YouTube视频的SRT...
echo =======================================
echo.

REM 创建日志文件
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "log_file=srt_download_%dt:~0,8%_%dt:~8,6%.log"
echo 📝 日志文件: %log_file%
echo.

REM 计数器
set /a success_count=0
set /a error_count=0
set /a total_count={len(video_ids)}

"""

    for index, video_id in enumerate(video_ids, 1):
        num = str(index).zfill(3)
        script += f"""
REM {num}. 视频ID: {video_id}
echo [{index}/{len(video_ids)}] 处理视频: {video_id}
echo 🔗 YouTube链接: https://www.youtube.com/watch?v={video_id}

REM 执行curl命令
curl -s -X POST https://lic.deepsrt.cc/webhook/get-srt-from-provider -H "Content-Type: application/json" -d "{{\\"youtube_id\\":\\"{video_id}\\", \\"fetch_only\\": \\"true\\"}}" > temp_response.txt 2>&1

if %errorlevel% equ 0 (
    echo ✅ 成功
    type temp_response.txt >> "%log_file%"
    set /a success_count+=1
) else (
    echo ❌ 失败
    type temp_response.txt >> "%log_file%"
    set /a error_count+=1
)

echo 进度: %success_count% 成功, %error_count% 失败
echo ---
timeout /t 1 /nobreak >nul

"""

    script += f"""
echo =======================================
echo 🎉 处理完成！
echo 📊 统计结果:
echo    总数: %total_count%
echo    成功: %success_count%
echo    失败: %error_count%
echo.
echo 📝 详细日志已保存到: %log_file%
del temp_response.txt 2>nul
pause
"""

    return script

def generate_powershell_script(video_ids):
    """生成PowerShell脚本"""
    script = f"""# YouTube SRT批量获取脚本 (PowerShell版本)
# 总共 {len(video_ids)} 个视频

Write-Host "🚀 开始处理 {len(video_ids)} 个YouTube视频的SRT..." -ForegroundColor Green
Write-Host "======================================="
Write-Host ""

# 创建日志文件
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "srt_download_$timestamp.log"
Write-Host "📝 日志文件: $logFile" -ForegroundColor Yellow
Write-Host ""

# 计数器
$successCount = 0
$errorCount = 0
$totalCount = {len(video_ids)}

"""

    for index, video_id in enumerate(video_ids, 1):
        num = str(index).zfill(3)
        script += f"""
# {num}. 视频ID: {video_id}
Write-Host "[{index}/{len(video_ids)}] 处理视频: {video_id}" -ForegroundColor Cyan
Write-Host "🔗 YouTube链接: https://www.youtube.com/watch?v={video_id}"

try {{
    # 执行curl命令
    $headers = @{{"Content-Type" = "application/json"}}
    $body = @{{"youtube_id" = "{video_id}"; "fetch_only" = "true"}} | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "https://lic.deepsrt.cc/webhook/get-srt-from-provider" -Method POST -Headers $headers -Body $body
    
    Write-Host "✅ 成功: $response" -ForegroundColor Green
    Add-Content -Path $logFile -Value "[{index}] {video_id}: SUCCESS - $response"
    $successCount++
}}
catch {{
    Write-Host "❌ 失败: $($_.Exception.Message)" -ForegroundColor Red
    Add-Content -Path $logFile -Value "[{index}] {video_id}: ERROR - $($_.Exception.Message)"
    $errorCount++
}}

Write-Host "进度: $successCount 成功, $errorCount 失败"
Write-Host "---"
Start-Sleep -Seconds 1

"""

    script += f"""
Write-Host "======================================="
Write-Host "🎉 处理完成！" -ForegroundColor Green
Write-Host "📊 统计结果:"
Write-Host "   总数: $totalCount"
Write-Host "   成功: $successCount"
Write-Host "   失败: $errorCount"
Write-Host "   成功率: $([math]::Round($successCount / $totalCount * 100, 2))%"
Write-Host ""
Write-Host "📝 详细日志已保存到: $logFile" -ForegroundColor Yellow
Read-Host "按回车键退出"
"""

    return script

def save_scripts(bash_script, windows_script, powershell_script, total_videos):
    """保存脚本到文件"""
    
    # 保存Bash脚本 - 修复newline问题
    with open('download_srt_batch.sh', 'w', encoding='utf-8') as f:
        f.write(bash_script)
    print(f"✅ 已生成 download_srt_batch.sh (Linux/Mac)")
    
    # 保存Windows批处理脚本
    with open('download_srt_batch.bat', 'w', encoding='utf-8') as f:
        f.write(windows_script)
    print(f"✅ 已生成 download_srt_batch.bat (Windows)")
    
    # 保存PowerShell脚本
    with open('download_srt_batch.ps1', 'w', encoding='utf-8') as f:
        f.write(powershell_script)
    print(f"✅ 已生成 download_srt_batch.ps1 (PowerShell)")
    
    print(f"""
🎉 脚本生成完成！共包含 {total_videos} 个视频的curl命令

📋 使用方法:
  Linux/Mac:   chmod +x download_srt_batch.sh && ./download_srt_batch.sh
  Windows:     download_srt_batch.bat
  PowerShell:  PowerShell -ExecutionPolicy Bypass -File download_srt_batch.ps1

⚠️  注意事项:
  - 请确保网络连接稳定
  - 脚本会自动添加延迟避免请求过于频繁
  - 所有操作都会记录到日志文件中
  - 建议在执行前测试几个视频ID
""")

if __name__ == "__main__":
    print("SRT批量下载脚本生成器")
    print("=" * 40)
    generate_curl_scripts()
