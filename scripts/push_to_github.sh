#!/bin/bash
# push_to_github.sh - 将晨报推送到 GitHub
# 由 cron 任务在生成晨报后调用
# 用法: push_to_github.sh <report_content_file> [report_date]

set -e

REPO_DIR="/tmp/wealth-invest-daily"
REPORT_FILE="$1"
REPORT_DATE="$2"

if [ -z "$REPORT_DATE" ]; then
    REPORT_DATE=$(date +%Y-%m-%d)
fi

# 检查晨报内容文件
if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ 晨报内容文件不存在: $REPORT_FILE"
    exit 1
fi

# 确保仓库存在
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "克隆仓库..."
    git clone git@github.com:corinwe/wealth-invest-daily.git "$REPO_DIR"
fi

cd "$REPO_DIR"

# 拉取最新状态（防止冲突）
git pull --rebase origin main 2>/dev/null || true

# 复制晨报到 reports 目录
mkdir -p reports
cp "$REPORT_FILE" "reports/${REPORT_DATE}.md"

# 配置 git
git config user.name "Hermes Agent (九九)"
git config user.email "corin@offerpath.com"

# 提交并推送
git add reports/${REPORT_DATE}.md
git add README.md 2>/dev/null || true

if git diff --cached --quiet; then
    echo "ℹ️  没有新的变更"
else
    git commit -m "📈 九九财富投资晨报 - ${REPORT_DATE}"
    git push origin main
    echo "✅ 晨报已推送: https://github.com/corinwe/wealth-invest-daily/blob/main/reports/${REPORT_DATE}.md"
fi
