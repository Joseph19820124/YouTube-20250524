#!/bin/bash
# YouTube多频道处理后台运行脚本

# 设置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/youtube_processing.pid"
MAIN_SCRIPT="$SCRIPT_DIR/get_all_videos.py"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 生成带时间戳的日志文件名
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_LOG="$LOG_DIR/youtube_output_$TIMESTAMP.log"
ERROR_LOG="$LOG_DIR/youtube_error_$TIMESTAMP.log"
COMBINED_LOG="$LOG_DIR/youtube_combined_$TIMESTAMP.log"

# 函数：启动程序
start_processing() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "❌ 程序已在运行中，PID: $(cat "$PID_FILE")"
        echo "如需重启，请先运行: $0 stop"
        exit 1
    fi

    echo "🚀 启动YouTube多频道处理程序（后台模式）..."
    echo "📁 工作目录: $SCRIPT_DIR"
    echo "📝 输出日志: $OUTPUT_LOG"
    echo "❌ 错误日志: $ERROR_LOG"
    echo "📋 合并日志: $COMBINED_LOG"
    
    # 后台运行程序
    nohup python3 "$MAIN_SCRIPT" > "$OUTPUT_LOG" 2> "$ERROR_LOG" &
    
    # 保存PID
    echo $! > "$PID_FILE"
    
    # 同时创建合并日志的进程
    {
        tail -f "$OUTPUT_LOG" 2>/dev/null &
        tail -f "$ERROR_LOG" 2>/dev/null &
        wait
    } > "$COMBINED_LOG" &
    
    echo "✅ 程序已启动，PID: $(cat "$PID_FILE")"
    echo ""
    echo "📊 监控命令:"
    echo "  查看实时日志: tail -f $COMBINED_LOG"
    echo "  查看输出日志: tail -f $OUTPUT_LOG"
    echo "  查看错误日志: tail -f $ERROR_LOG"
    echo "  检查进程状态: $0 status"
    echo "  停止程序: $0 stop"
}

# 函数：停止程序
stop_processing() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ 没有找到PID文件，程序可能没有运行"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "🛑 正在停止程序，PID: $PID"
        kill "$PID"
        
        # 等待程序停止
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            echo "⏳ 等待程序停止... ($i/10)"
            sleep 1
        done
        
        # 如果还没停止，强制杀死
        if kill -0 "$PID" 2>/dev/null; then
            echo "⚡ 强制终止程序"
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        echo "✅ 程序已停止"
    else
        echo "❌ 程序已经停止，清理PID文件"
        rm -f "$PID_FILE"
    fi
}

# 函数：检查状态
check_status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        PID=$(cat "$PID_FILE")
        echo "✅ 程序正在运行，PID: $PID"
        
        # 显示进程信息
        echo "📊 进程信息:"
        ps -p "$PID" -o pid,ppid,cmd,etime,pcpu,pmem
        
        # 显示最新日志
        LATEST_LOG=$(find "$LOG_DIR" -name "youtube_combined_*.log" -type f -printf '%T@ %p\n' | sort -k 1nr | head -1 | cut -d' ' -f2-)
        if [ -n "$LATEST_LOG" ] && [ -f "$LATEST_LOG" ]; then
            echo ""
            echo "📝 最新日志 (最后10行):"
            tail -10 "$LATEST_LOG"
            echo ""
            echo "💡 实时监控: tail -f $LATEST_LOG"
        fi
    else
        echo "❌ 程序没有在运行"
        if [ -f "$PID_FILE" ]; then
            echo "🧹 清理过期的PID文件"
            rm -f "$PID_FILE"
        fi
        return 1
    fi
}

# 函数：查看日志
view_logs() {
    echo "📂 日志文件列表:"
    find "$LOG_DIR" -name "youtube_*.log" -type f -printf '%TY-%Tm-%Td %TH:%TM  %s bytes  %p\n' | sort -r
    
    echo ""
    echo "📝 查看日志命令:"
    echo "  实时查看最新合并日志: tail -f $LOG_DIR/youtube_combined_*.log | head -1"
    echo "  查看所有输出日志: ls $LOG_DIR/youtube_output_*.log"
    echo "  查看所有错误日志: ls $LOG_DIR/youtube_error_*.log"
}

# 函数：清理日志
clean_logs() {
    echo "🧹 清理日志文件..."
    
    # 保留最近7天的日志
    find "$LOG_DIR" -name "youtube_*.log" -type f -mtime +7 -delete
    
    echo "✅ 清理完成"
    view_logs
}

# 函数：显示帮助
show_help() {
    echo "🎬 YouTube多频道处理后台运行管理脚本"
    echo ""
    echo "用法: $0 {start|stop|restart|status|logs|clean|help}"
    echo ""
    echo "命令说明:"
    echo "  start    - 启动程序（后台运行）"
    echo "  stop     - 停止程序"
    echo "  restart  - 重启程序"
    echo "  status   - 查看运行状态"
    echo "  logs     - 查看日志文件列表"
    echo "  clean    - 清理旧日志文件（保留7天）"
    echo "  help     - 显示此帮助信息"
    echo ""
    echo "📁 日志目录: $LOG_DIR"
    echo "📝 PID文件: $PID_FILE"
}

# 主逻辑
case "$1" in
    start)
        start_processing
        ;;
    stop)
        stop_processing
        ;;
    restart)
        stop_processing
        sleep 2
        start_processing
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    clean)
        clean_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ 无效参数: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
