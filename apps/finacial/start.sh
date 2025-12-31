#!/bin/bash
# 财务报表分析系统 - 快速启动脚本 (Linux/macOS)

echo "========================================"
echo "财务报表分析系统"
echo "========================================"
echo ""

# 检查 Poetry 是否安装
if ! command -v poetry &> /dev/null; then
    echo "[错误] 未检测到 Poetry，请先安装 Poetry"
    echo "安装命令: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "[1/4] 检查并安装依赖..."
poetry install

if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo ""
echo "[2/4] 检查 Playwright 浏览器..."
if ! poetry run playwright --version &> /dev/null; then
    echo "[提示] 首次运行需要安装 Playwright 浏览器（约 100MB）"
    echo "正在安装 Chromium 浏览器..."
    poetry run playwright install chromium
    if [ $? -ne 0 ]; then
        echo "[错误] Playwright 浏览器安装失败"
        exit 1
    fi
    echo "Playwright 浏览器安装完成！"
else
    echo "Playwright 浏览器已安装"
fi

echo ""
echo "[3/4] 启动服务器..."
echo "访问地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "[4/4] 按 Ctrl+C 停止服务器"
echo ""

poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

