# 财务报表分析系统

基于 LangChain 的智能财务报表分析系统，支持自动爬取、下载和 AI 分析上市公司财务报表。

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [API 文档](#api-文档)
- [依赖管理](#依赖管理)

## ✨ 功能特性

- 🔍 自动爬取上海、深圳、北京交易所的财务报表
- 📥 智能下载和缓存 PDF 文件
- 🤖 基于 LangChain 的 AI 智能分析
- 📊 支持流式响应，实时返回分析进度
- 💾 数据库缓存，避免重复爬取
- 🚀 FastAPI 构建的高性能 API

## 🚀 快速开始

### 方式一：使用 Poetry（推荐）

```bash
# 1. 安装 Poetry（如果未安装）
# Windows PowerShell:
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Linux/macOS:
curl -sSL https://install.python-poetry.org | python3 -

# 2. 安装依赖
cd d:\python-playground\langchain\financial
poetry install

# 3. 安装 Playwright 浏览器（重要！）
poetry run playwright install chromium

# 4. 启动服务器
poetry run uvicorn main:app --reload

# 或者使用快速启动脚本（自动完成所有步骤）
# Windows:
start.bat

# Linux/macOS:
chmod +x start.sh
./start.sh
```

### 方式二：使用 pip

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器（重要！）
playwright install chromium

# 5. 启动服务器
uvicorn main:app --reload
```

> **⚠️ 重要提示:** Playwright 需要单独安装浏览器二进制文件，详见 [INSTALL.md](./INSTALL.md)

### 访问服务

- API 地址: http://localhost:8000
- Swagger 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

## 📁 项目结构

```
financial/
├── main.py                 # FastAPI 主入口
├── index.py                # 核心业务逻辑
├── pyproject.toml          # Poetry 配置文件
├── requirements.txt        # pip 依赖文件
├── cookie.json             # 认证 Cookie
├── ai/                     # AI 分析模块
│   ├── analyse_pdf.py      # PDF 分析
│   └── index.py            # AI 主逻辑
├── crawler_website/        # 网页爬虫模块
│   ├── run_browser.py      # 浏览器控制
│   ├── shanghai.py         # 上海交易所
│   ├── shengzhen.py        # 深圳交易所
│   └── beijing.py          # 北京交易所
├── download_pdf/           # PDF 下载模块
│   └── auth_download.py    # 认证下载
├── db/                     # 数据库模块
│   ├── save_company_info.py # 保存公司信息
│   └── search_SQL.py       # 查询数据
└── pdf/                    # PDF 存储目录
```

## 📖 API 文档

### POST /analyze

分析财务报表（流式响应）

**请求体：**

```json
{
  "exchange_code": "SH",
  "stock_code": "601127",
  "fiscal_year": 2024,
  "company_name": "",
  "period_type": 3
}
```

**参数说明：**

- `exchange_code`: 交易所代码（SH=上海, SZ=深圳, BJ=北京）
- `stock_code`: 股票代码
- `fiscal_year`: 财政年份
- `company_name`: 公司名称（可选）
- `period_type`: 报表类型（1=一季报, 2=半年报, 3=三季报, 4=年报）

**响应格式（SSE 流式）：**

```json
// 进度事件
{"status": "progress", "step": "query", "message": "正在查询数据库..."}
{"status": "progress", "step": "download", "message": "正在下载 PDF..."}

// 分析事件
{"status": "analyzing", "step": "analysis_stream", "data": "分析内容..."}

// 完成事件
{"status": "complete", "message": "分析完成", "data": {...}}
```

### GET /health

健康检查

**响应：**

```json
{ "status": "healthy" }
```

## 🛠️ 依赖管理

### 使用 Poetry（推荐）

```bash
# 添加依赖
poetry add package-name

# 添加开发依赖
poetry add --group dev pytest

# 更新依赖
poetry update

# 查看依赖
poetry show --tree

# 导出 requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

详细指南请查看：[POETRY_GUIDE.md](./POETRY_GUIDE.md)

### 使用 pip

```bash
# 安装依赖
pip install -r requirements.txt

# 更新依赖
pip install --upgrade package-name

# 冻结依赖
pip freeze > requirements.txt
```

## 🔧 配置

### 环境变量

创建 `.env` 文件：

```env
# OpenAI API
OPENAI_API_KEY=your-api-key-here

# Supabase（如果使用）
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# 其他配置
LOG_LEVEL=INFO
```

### Cookie 配置

编辑 `cookie.json` 文件，添加必要的认证信息。

## 📝 开发

### 代码格式化

```bash
# 使用 Poetry
poetry run black .
poetry run flake8 .

# 使用 pip
pip install black flake8
black .
flake8 .
```

### 运行测试

```bash
# 使用 Poetry
poetry run pytest

# 使用 pip
pip install pytest
pytest
```

## 🐛 常见问题

### Q: Poetry 安装很慢？

A: 配置国内镜像源

```bash
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/
```

### Q: 如何切换 Python 版本？

A: 使用 Poetry 指定版本

```bash
poetry env use python3.10
```

### Q: PDF 下载失败？

A: 检查 `cookie.json` 是否配置正确，或者网络连接是否正常。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请联系项目维护者。
