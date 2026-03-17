#!/bin/bash
# 加密货币监控定时任务
# 每小时运行一次市场分析

echo "🚀 启动加密货币监控服务..."
echo "⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 工作目录
cd /root/.openclaw/workspace/crypto-monitor

# 创建日志目录
mkdir -p logs

# 运行分析
LOG_FILE="logs/monitor_$(date '+%Y%m%d_%H%M%S').log"

echo "📊 开始市场分析..." | tee -a "$LOG_FILE"
python3 monitor.py 2>&1 | tee -a "$LOG_FILE"

echo "✅ 分析完成！" | tee -a "$LOG_FILE"
echo "📄 日志文件: $LOG_FILE" | tee -a "$LOG_FILE"

# 发送通知（如果需要的话）
# 可以在这里添加 Feishu/Telegram/邮件通知

echo "🎉 监控服务运行完成！"
