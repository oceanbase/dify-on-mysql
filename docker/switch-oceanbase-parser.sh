#!/bin/bash

# OceanBase分词器切换脚本
# 用于在ik和thai_ftparser之间切换

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

echo "=== OceanBase 分词器切换工具 ==="
echo

# 检查.env文件是否存在
if [[ ! -f "$ENV_FILE" ]]; then
    echo "错误: .env 文件不存在"
    exit 1
fi

echo "✓ 找到 .env 文件"

# 获取用户选择
while true; do
    read -p "是否使用泰语分词器? [y/N]: " choice
    case $choice in
        [Yy]* )
            NEW_PARSER="thai_ftparser"
            NEW_HYBRID="true"
            echo "✓ 选择了泰语分词器"
            break
            ;;
        [Nn]* | "" )
            NEW_PARSER="ik"
            NEW_HYBRID="false"
            echo "✓ 选择了IK分词器"
            break
            ;;
        * )
            echo "请输入 y 或 n"
            ;;
    esac
done

echo
echo "更新配置中..."

# 更新或添加 OCEANBASE_FULLTEXT_PARSER
if grep -q "^OCEANBASE_FULLTEXT_PARSER=" "$ENV_FILE"; then
    sed -i "s/^OCEANBASE_FULLTEXT_PARSER=.*/OCEANBASE_FULLTEXT_PARSER=$NEW_PARSER/" "$ENV_FILE"
    echo "✓ 已更新 OCEANBASE_FULLTEXT_PARSER=$NEW_PARSER"
else
    echo "OCEANBASE_FULLTEXT_PARSER=$NEW_PARSER" >> "$ENV_FILE"
    echo "✓ 已添加 OCEANBASE_FULLTEXT_PARSER=$NEW_PARSER"
fi

# 更新或添加 OCEANBASE_ENABLE_HYBRID_SEARCH
if grep -q "^OCEANBASE_ENABLE_HYBRID_SEARCH=" "$ENV_FILE"; then
    sed -i "s/^OCEANBASE_ENABLE_HYBRID_SEARCH=.*/OCEANBASE_ENABLE_HYBRID_SEARCH=$NEW_HYBRID/" "$ENV_FILE"
    echo "✓ 已更新 OCEANBASE_ENABLE_HYBRID_SEARCH=$NEW_HYBRID"
else
    echo "OCEANBASE_ENABLE_HYBRID_SEARCH=$NEW_HYBRID" >> "$ENV_FILE"
    echo "✓ 已添加 OCEANBASE_ENABLE_HYBRID_SEARCH=$NEW_HYBRID"
fi

echo
echo "=== 配置更新完成 ==="
echo "分词器: $NEW_PARSER"
echo "混合搜索: $NEW_HYBRID"
echo
echo "配置更改后需要重启相关服务: docker-compose restart api worker worker_beat"
