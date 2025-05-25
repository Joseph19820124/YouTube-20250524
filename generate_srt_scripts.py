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
# 生成时间: $(TZ='Asia/Shanghai' date)

echo "🚀 开始处理 {len(video_ids)} 个YouTube视频的SRT..."
echo "======================================="
echo ""

# 创建日志文件
log_file="srt_download_$(TZ='Asia/Shanghai' date +%Y%m%d_%H%M%S).log"
echo "📝 日志文件: $log_file"
echo ""

# 计数器
success_count=0
error_count=0
total_count={len(video_ids)}

# 记录开始时间
start_time=$(TZ='Asia/Shanghai' date)
echo "🕐 开始时间: $start_time" | tee -a "$log_file"
echo "=======================================" | tee -a "$log_file"

"""

    for index, video_id in enumerate(video_ids, 1):
        num = str(index).zfill(3)
        script += f"""
# {num}. 视频ID: {video_id}
echo "[{index}/{len(video_ids)}] 处理视频: {video_id}"
echo "🔗 YouTube链接: https://www.youtube.com/watch?v={video_id}"

# 第一次执行curl命令 (fetch_only: true)
echo "🔍 第一次尝试获取缓存..."
response=$(curl -s -X POST https://lic.deepsrt.cc/webhook/get-srt-from-provider \\
    -H "Content-Type: application/json" \\
    -d '{{"youtube_id":"{video_id}", "fetch_only": "true"}}' \\
    -w "\\n%{{http_code}}")

# 检查响应状态
http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    # 检查是否返回 "not cached"
    if echo "$response_body" | grep -q '"status":"not cached"'; then
        echo "⚠️  缓存未找到，开始重新生成SRT..."
        echo "⚠️  [{index}] 缓存未找到: $response_body [$(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S %Z')]" | tee -a "$log_file"
        
        # 第二次执行curl命令 (fetch_only: false)
        echo "🔄 第二次尝试生成SRT..."
        response2=$(curl -s -X POST https://lic.deepsrt.cc/webhook/get-srt-from-provider \\
            -H "Content-Type: application/json" \\
            -d '{{"youtube_id":"{video_id}", "fetch_only": "false"}}' \\
            -w "\\n%{{http_code}}")
        
        # 检查第二次响应状态
        http_code2=$(echo "$response2" | tail -n1)
        response_body2=$(echo "$response2" | head -n -1)
        
        if [ "$http_code2" = "200" ]; then
            echo "✅ [{index}] 生成成功: $response_body2 [$(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S %Z')]" | tee -a "$log_file"
            ((success_count++))
        else
            echo "❌ [{index}] 生成失败 (HTTP $http_code2): $response_body2 [$(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S %Z')]" | tee -a "$log_file"
            ((error_count++))
        fi
    else
        echo "✅ [{index}] 缓存成功: $response_body [$(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S %Z')]" | tee -a "$log_file"
        ((success_count++))
    fi
else
    echo "❌ [{index}] 请求失败 (HTTP $http_code): $response_body [$(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S %Z')]" | tee -a "$log_file"
    ((error_count++))
fi

echo "📊 进度: $success_count 成功, $error_count 失败, 剩余 $(( total_count - {index} )) 个"
echo "⏱️  完成度: $(( {index} * 100 / total_count ))%" | tee -a "$log_file"
echo "---"
sleep 1  # 避免请求过于频繁

"""

    script += f"""
echo "======================================="
echo "🎉 处理完成！"
end_time=$(TZ='Asia/Shanghai' date)
echo "🕐 结束时间: $end_time" | tee -a "$log_file"
echo "📊 统计结果:" | tee -a "$log_file"
echo "   总数: $total_count" | tee -a "$log_file"
echo "   成功: $success_count" | tee -a "$log_file"
echo "   失败: $error_count" | tee -a "$log_file"
echo "   成功率: $(( success_count * 100 / total_count ))%" | tee -a "$log_file"
echo ""
echo "📝 详细日志已保存到: $log_file"
echo "=======================================" | tee -a "$log_file"
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

REM 设置中国时区 (UTC+8)
REM 获取UTC+8时间
for /f "tokens=1-3 delims=." %%a in ('powershell -command "(Get-Date).ToUniversalTime().AddHours(8).ToString('yyyy.MM.dd')"') do set "utc8_date=%%a-%%b-%%c"
for /f "tokens=1" %%a in ('powershell -command "(Get-Date).ToUniversalTime().AddHours(8).ToString('HH:mm:ss')"') do set "utc8_time=%%a"

REM 创建日志文件
for /f "tokens=1" %%a in ('powershell -command "(Get-Date).ToUniversalTime().AddHours(8).ToString('yyyyMMdd_HHmmss')"') do set "timestamp=%%a"
set "log_file=srt_download_%timestamp%.log"
echo 📝 日志文件: %log_file%
echo.

REM 计数器
set /a success_count=0
set /a error_count=0
set /a total_count={len(video_ids)}

REM 记录开始时间
echo 🕐 开始时间: %utc8_date% %utc8_time% CST >> "%log_file%"
echo ======================================= >> "%log_file%"

"""

    for index, video_id in enumerate(video_ids, 1):
        num = str(index).zfill(3)
        remaining = len(video_ids) - index
        progress = int((index / len(video_ids)) * 100)
        
        script += f"""
REM {num}. 视频ID: {video_id}
echo [{index}/{len(video_ids)}] 处理视频: {video_id}
echo 🔗 YouTube链接: https://www.youtube.com/watch?v={video_id}

REM 获取当前UTC+8时间
for /f "tokens=1-3 delims=." %%a in ('powershell -command "(Get-Date).ToUniversalTime().AddHours(8).ToString('yyyy.MM.dd')"') do set "current_date=%%a-%%b-%%c"
for /f "tokens=1" %%a in ('powershell -command "(Get-Date).ToUniversalTime().AddHours(8).ToString('HH:mm:ss')"') do set "current_time=%%a"

REM 第一次执行curl命令 (fetch_only: true)
echo 🔍 第一次尝试获取缓存...
curl -s -X POST https://lic.deepsrt.cc/webhook/get-srt-from-provider -H "Content-Type: application/json" -d "{{\\\"youtube_id\\\":\\\"{video_id}\\\", \\\"fetch_only\\\": \\\"true\\\"}}" > temp_response.txt 2>&1

if %errorlevel% equ 0 (
    REM 检查是否返回 "not cached"
    findstr /C:"\\"status\\":\\"not cached\\"" temp_response.txt >nul
    if %errorlevel% equ 0 (
        echo ⚠️  缓存未找到，开始重新生成SRT...
        echo ⚠️  [{index}] 缓存未找到 [%current_date% %current_time% CST]: >> "%log_file%"
        type temp_response.txt >> "%log_file%"
        
        REM 第二次执行curl命令 (fetch_only: false)
        echo 🔄 第二次尝试生成SRT...
        curl -s -X POST https://lic.deepsrt.cc/webhook/get-srt-from-provider -H "Content-Type: application/json" -d "{{\\\"youtube_id\\\":\\\"{video_id}\\\", \\\"fetch_only\\\": \\\"false\\\"}}" > temp_response2.txt 2>&1
        
        if %errorlevel% equ 0 (
            echo ✅ [{index}] 生成成功 [%current_date% %current_time% CST]
            echo ✅ [{index}] 生成成功 [%current_date% %current_time% CST]: >> "%log_file%"
            type temp_response2.txt >> "%log_file%"
            set /a success_count+=1
        ) else (
            echo ❌ [{index}] 生成失败 [%current_date% %current_time% CST]
            echo ❌ [{index}] 生成失败 [%current_date% %current_time% CST]: >> "%log_file%"
            type temp_response2.txt >> "%log_file%"
            set /a error_count+=1
        )
        del temp_response2.txt 2>nul
    ) else (
        echo ✅ [{index}] 缓存成功 [%current_date% %current_time% CST]
        echo ✅ [{index}] 缓存成功 [%current_date% %current_time% CST]: >> "%log_file%"
        type temp_response.txt >> "%log_file%"
        set /a success_count+=1
    )
) else (
    echo ❌ [{index}] 请求失败 [%current_date% %current_time% CST]
    echo ❌ [{index}] 请求失败 [%current_date% %current_time% CST]: >> "%log_file%"
    type temp_response.txt >> "%log_file%"
    set /a error_count+=1
)

echo 📊 进度: %success_count% 成功, %error_count% 失败, 剩余 {remaining} 个
echo ⏱️  完成度: {progress}%% >> "%log_file%"
echo ---
timeout /t 1 /nobreak >nul

"""

    script += f"""
REM 获取结束时间
for /f "tokens=1-3 delims=." %%a in ('powershell -command "(Get-Date).ToUniversalTime().AddHours(8).ToString('yyyy.MM.dd')"') do set "end_date=%%a-%%b-%%c"
for /f "tokens=1" %%a in ('powershell -command "(Get-Date).ToUniversalTime().AddHours(8).ToString('HH:mm:ss')"') do set "end_time=%%a"

echo =======================================
echo 🎉 处理完成！
echo 🕐 结束时间: %end_date% %end_time% CST >> "%log_file%"
echo 📊 统计结果: >> "%log_file%"
echo    总数: %total_count% >> "%log_file%"
echo    成功: %success_count% >> "%log_file%"
echo    失败: %error_count% >> "%log_file%"
echo. >> "%log_file%"
echo 📝 详细日志已保存到: %log_file%
echo ======================================= >> "%log_file%"
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

# 设置中国时区 (UTC+8)
$chinaTimeZone = [System.TimeZoneInfo]::FindSystemTimeZoneById("China Standard Time")

# 创建日志文件
$timestamp = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), $chinaTimeZone).ToString("yyyyMMdd_HHmmss")
$logFile = "srt_download_$timestamp.log"
Write-Host "📝 日志文件: $logFile" -ForegroundColor Yellow
Write-Host ""

# 计数器
$successCount = 0
$errorCount = 0
$totalCount = {len(video_ids)}

# 记录开始时间
$startTime = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), $chinaTimeZone).ToString("yyyy-MM-dd HH:mm:ss")
"🕐 开始时间: $startTime CST" | Add-Content -Path $logFile
"=======================================" | Add-Content -Path $logFile

"""

    for index, video_id in enumerate(video_ids, 1):
        num = str(index).zfill(3)
        remaining = len(video_ids) - index
        progress = round((index / len(video_ids)) * 100, 1)
        
        script += f"""
# {num}. 视频ID: {video_id}
Write-Host "[{index}/{len(video_ids)}] 处理视频: {video_id}" -ForegroundColor Cyan
Write-Host "🔗 YouTube链接: https://www.youtube.com/watch?v={video_id}"

try {{
    # 第一次执行curl命令 (fetch_only: true)
    Write-Host "🔍 第一次尝试获取缓存..." -ForegroundColor Yellow
    $headers = @{{"Content-Type" = "application/json"}}
    $body1 = @{{"youtube_id" = "{video_id}"; "fetch_only" = "true"}} | ConvertTo-Json
    
    $response1 = Invoke-RestMethod -Uri "https://lic.deepsrt.cc/webhook/get-srt-from-provider" -Method POST -Headers $headers -Body $body1
    
    $timestamp = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), $chinaTimeZone).ToString("yyyy-MM-dd HH:mm:ss")
    
    # 检查是否返回 "not cached"
    if ($response1 -match '"status":"not cached"') {{
        Write-Host "⚠️  缓存未找到，开始重新生成SRT..." -ForegroundColor Yellow
        Add-Content -Path $logFile -Value "⚠️  [{index}] 缓存未找到: $response1 [$timestamp CST]"
        
        try {{
            # 第二次执行curl命令 (fetch_only: false)
            Write-Host "🔄 第二次尝试生成SRT..." -ForegroundColor Yellow
            $body2 = @{{"youtube_id" = "{video_id}"; "fetch_only" = "false"}} | ConvertTo-Json
            
            $response2 = Invoke-RestMethod -Uri "https://lic.deepsrt.cc/webhook/get-srt-from-provider" -Method POST -Headers $headers -Body $body2
            
            $timestamp2 = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), $chinaTimeZone).ToString("yyyy-MM-dd HH:mm:ss")
            Write-Host "✅ [{index}] 生成成功: $response2 [$timestamp2 CST]" -ForegroundColor Green
            Add-Content -Path $logFile -Value "✅ [{index}] 生成成功: $response2 [$timestamp2 CST]"
            $successCount++
        }}
        catch {{
            $timestamp2 = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), $chinaTimeZone).ToString("yyyy-MM-dd HH:mm:ss")
            Write-Host "❌ [{index}] 生成失败: $($_.Exception.Message) [$timestamp2 CST]" -ForegroundColor Red
            Add-Content -Path $logFile -Value "❌ [{index}] 生成失败: $($_.Exception.Message) [$timestamp2 CST]"
            $errorCount++
        }}
    }}
    else {{
        Write-Host "✅ [{index}] 缓存成功: $response1 [$timestamp CST]" -ForegroundColor Green
        Add-Content -Path $logFile -Value "✅ [{index}] 缓存成功: $response1 [$timestamp CST]"
        $successCount++
    }}
}}
catch {{
    $timestamp = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), $chinaTimeZone).ToString("yyyy-MM-dd HH:mm:ss")
    Write-Host "❌ [{index}] 请求失败: $($_.Exception.Message) [$timestamp CST]" -ForegroundColor Red
    Add-Content -Path $logFile -Value "❌ [{index}] 请求失败: $($_.Exception.Message) [$timestamp CST]"
    $errorCount++
}}

Write-Host "📊 进度: $successCount 成功, $errorCount 失败, 剩余 {remaining} 个"
Add-Content -Path $logFile -Value "⏱️  完成度: {progress}%"
Write-Host "---"
Start-Sleep -Seconds 1

"""

    script += f"""
Write-Host "======================================="
Write-Host "🎉 处理完成！" -ForegroundColor Green
$endTime = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), $chinaTimeZone).ToString("yyyy-MM-dd HH:mm:ss")
"🕐 结束时间: $endTime CST" | Add-Content -Path $logFile
"📊 统计结果:" | Add-Content -Path $logFile
"   总数: $totalCount" | Add-Content -Path $logFile
"   成功: $successCount" | Add-Content -Path $logFile
"   失败: $errorCount" | Add-Content -Path $logFile
"   成功率: $([math]::Round($successCount / $totalCount * 100, 2))%" | Add-Content -Path $logFile

Write-Host "📊 统计结果:"
Write-Host "   总数: $totalCount"
Write-Host "   成功: $successCount"
Write-Host "   失败: $errorCount"
Write-Host "   成功率: $([math]::Round($successCount / $totalCount * 100, 2))%"
Write-Host ""
Write-Host "📝 详细日志已保存到: $logFile" -ForegroundColor Yellow
"=======================================" | Add-Content -Path $logFile
Read-Host "按回车键退出"
"""

    return script

def save_scripts(bash_script, windows_script, powershell_script, total_videos):
    """保存脚本到文件"""
    
    # 保存Bash脚本
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
  Linux/Mac:   chmod +x download_srt_batch.sh && nohup ./download_srt_batch.sh > srt_download.log 2>&1 &
  Windows:     download_srt_batch.bat
  PowerShell:  PowerShell -ExecutionPolicy Bypass -File download_srt_batch.ps1

📊 输出示例:
  🔍 第一次尝试获取缓存...
  ⚠️  缓存未找到，开始重新生成SRT...
  🔄 第二次尝试生成SRT...
  ✅ [156] 生成成功: {{"status": "success"}} [2025-05-25 15:30:42 CST]
  或
  ✅ [157] 缓存成功: {{"status": "cached"}} [2025-05-25 15:30:43 CST]

⚠️  注意事项:
  - 请确保网络连接稳定
  - 脚本会自动处理缓存未命中的情况
  - 如果缓存不存在，会自动尝试重新生成SRT
  - 所有操作都会记录到日志文件中
  - 所有时间戳均使用中国标准时间 (UTC+8 CST)
""")

if __name__ == "__main__":
    print("SRT批量下载脚本生成器")
    print("=" * 40)
    generate_curl_scripts()
