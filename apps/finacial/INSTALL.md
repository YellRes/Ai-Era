# 安装指南

## 📦 完整安装步骤

### 方式一：使用 Poetry（推荐）

#### 1. 安装 Poetry

**Windows (PowerShell):**

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Linux/macOS:**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**验证安装:**

```bash
poetry --version
```

#### 2. 安装项目依赖

```bash
cd d:\python-playground\langchain\financial
poetry install
```

#### 3. 安装 Playwright 浏览器（重要！）

```bash
# 使用 Poetry 运行
poetry run playwright install chromium

# 或者进入虚拟环境后运行
poetry shell
playwright install chromium
```

#### 4. 启动项目

```bash
# 方式1：使用快速启动脚本
start.bat

# 方式2：手动启动
poetry run uvicorn main:app --reload

# 方式3：进入虚拟环境
poetry shell
uvicorn main:app --reload
```

---

### 方式二：使用 pip

#### 1. 创建虚拟环境

```bash
cd d:\python-playground\langchain\financial
python -m venv venv
```

#### 2. 激活虚拟环境

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 安装 Playwright 浏览器（重要！）

```bash
playwright install chromium
```

#### 5. 启动项目

```bash
uvicorn main:app --reload
```

---

## 🔧 依赖说明

### 核心依赖

- **LangChain** - AI 框架
- **LangGraph** - 工作流编排
- **FastAPI** - Web 框架
- **Playwright** - 浏览器自动化（需要额外安装浏览器）
- **PyMuPDF** - PDF 处理
- **Sentence Transformers** - 中文 Embeddings
- **Supabase** - 数据库

### 为什么需要单独安装 Playwright 浏览器？

Playwright 需要下载浏览器二进制文件（Chromium），这不是 Python 包的一部分。

**安装命令:**

```bash
# 只安装 Chromium（推荐，体积小）
playwright install chromium

# 安装所有浏览器（可选）
playwright install
```

**验证安装:**

```bash
playwright --version
```

---

## 🐛 常见问题

### Q1: ModuleNotFoundError: No module named 'playwright'

**原因:** 没有安装 playwright 包

**解决方案:**

```bash
# Poetry
poetry add playwright
poetry run playwright install chromium

# pip
pip install playwright
playwright install chromium
```

### Q2: playwright.\_impl.\_errors.Error: Executable doesn't exist

**原因:** 没有安装 Playwright 浏览器

**解决方案:**

```bash
playwright install chromium
```

### Q3: 安装 Playwright 浏览器很慢

**原因:** 下载浏览器二进制文件需要时间（约 100-200MB）

**解决方案:**

- 耐心等待
- 或使用代理加速下载

### Q4: torch 安装失败或很慢

**原因:** PyTorch 包很大（约 2GB）

**解决方案:**

**使用清华镜像（推荐）:**

```bash
# Poetry
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/

# pip
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**或安装 CPU 版本（更小）:**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Q5: 虚拟环境在哪里？

**Poetry:**

```bash
# 查看虚拟环境路径
poetry env info --path

# 默认位置（Windows）:
# C:\Users\<用户名>\AppData\Local\pypoetry\Cache\virtualenvs\
```

**pip venv:**

```bash
# 在项目目录的 venv 文件夹
d:\python-playground\langchain\financial\venv\
```

---

## 📋 完整安装检查清单

安装完成后，请检查以下内容：

- [ ] Python 3.9+ 已安装
- [ ] Poetry 或 pip 已安装
- [ ] 项目依赖已安装（`poetry install` 或 `pip install -r requirements.txt`）
- [ ] Playwright 浏览器已安装（`playwright install chromium`）
- [ ] 环境变量已配置（`.env` 文件）
- [ ] Cookie 已配置（`cookie.json` 文件）
- [ ] 服务器可以启动（`uvicorn main:app --reload`）
- [ ] 访问 http://localhost:8000/docs 可以看到 API 文档

---

## 🚀 快速测试

安装完成后，运行以下命令测试：

```bash
# 1. 检查健康状态
curl http://localhost:8000/health

# 2. 测试 API（使用 PowerShell）
$body = @{
    exchange_code = "SH"
    stock_code = "601127"
    fiscal_year = 2024
    period_type = 3
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/analyze" -Method POST -Body $body -ContentType "application/json"
```

---

## 📞 需要帮助？

如果遇到问题：

1. 查看本文档的常见问题部分
2. 查看 `POETRY_GUIDE.md` 了解 Poetry 详细用法
3. 查看 `README.md` 了解项目结构
4. 检查终端错误信息
5. 联系项目维护者

---

## 🎉 安装成功！

如果所有检查都通过，恭喜你！现在可以：

- 访问 http://localhost:8000/docs 查看 API 文档
- 开始使用财务报表分析功能
- 查看 `README.md` 了解更多功能
