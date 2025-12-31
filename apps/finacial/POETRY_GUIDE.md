# Poetry 使用指南

## 📦 Poetry 简介

Poetry 是现代化的 Python 依赖管理和打包工具，相比 pip + requirements.txt 有以下优势：

- ✅ 自动解决依赖冲突
- ✅ 锁定依赖版本（poetry.lock）
- ✅ 虚拟环境管理
- ✅ 项目打包和发布
- ✅ 开发/生产依赖分离

## 🚀 安装 Poetry

### Windows (PowerShell)
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Linux/macOS
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 验证安装
```bash
poetry --version
```

## 📋 项目迁移步骤

### 1. 初始化项目（已完成）
项目已经创建了 `pyproject.toml` 文件，包含所有依赖。

### 2. 安装依赖
```bash
# 进入项目目录
cd d:\python-playground\langchain\financial

# 安装所有依赖（会自动创建虚拟环境）
poetry install
```

### 3. 激活虚拟环境
```bash
# 方式1：进入虚拟环境 shell
poetry shell

# 方式2：在虚拟环境中运行命令
poetry run python main.py
poetry run uvicorn main:app --reload
```

## 🛠️ 常用命令

### 依赖管理
```bash
# 添加新依赖
poetry add requests

# 添加开发依赖
poetry add --group dev pytest

# 删除依赖
poetry remove requests

# 更新依赖
poetry update

# 更新特定包
poetry update langchain

# 查看已安装的包
poetry show

# 查看依赖树
poetry show --tree
```

### 虚拟环境管理
```bash
# 查看虚拟环境信息
poetry env info

# 查看虚拟环境路径
poetry env list

# 删除虚拟环境
poetry env remove python

# 使用特定 Python 版本
poetry env use python3.10
```

### 运行项目
```bash
# 启动 FastAPI 服务器
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或者先进入 shell
poetry shell
uvicorn main:app --reload
```

### 导出依赖
```bash
# 导出为 requirements.txt（兼容旧项目）
poetry export -f requirements.txt --output requirements.txt --without-hashes

# 包含开发依赖
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
```

## 📝 配置 Poetry

### 修改虚拟环境位置（可选）
```bash
# 在项目目录创建 .venv
poetry config virtualenvs.in-project true

# 查看配置
poetry config --list
```

### 配置国内镜像（加速下载）
```bash
# 配置清华镜像
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/

# 或者阿里云镜像
poetry source add --priority=primary aliyun https://mirrors.aliyun.com/pypi/simple/
```

## 🔄 从 requirements.txt 迁移

如果你想完全迁移到 Poetry：

```bash
# 1. 备份旧的 requirements.txt
cp requirements.txt requirements.txt.bak

# 2. 使用 Poetry 安装
poetry install

# 3. 测试项目是否正常运行
poetry run python main.py

# 4. 确认无误后，可以删除旧的 requirements.txt（可选）
# rm requirements.txt
```

## 🎯 推荐工作流

### 日常开发
```bash
# 1. 启动项目
cd d:\python-playground\langchain\financial
poetry shell

# 2. 运行服务器
uvicorn main:app --reload

# 3. 添加新依赖时
poetry add package-name

# 4. 退出虚拟环境
exit
```

### 团队协作
```bash
# 1. 克隆项目后
git clone <repo>
cd financial

# 2. 安装依赖（根据 poetry.lock）
poetry install

# 3. 开发完成后，提交 poetry.lock
git add pyproject.toml poetry.lock
git commit -m "feat: 更新依赖"
```

## ⚠️ 注意事项

1. **poetry.lock 文件**
   - 这个文件锁定了精确的依赖版本
   - 应该提交到 Git（保证团队环境一致）
   - 不要手动编辑

2. **虚拟环境**
   - Poetry 会自动创建和管理虚拟环境
   - 不需要手动 `python -m venv`

3. **依赖冲突**
   - Poetry 会自动解决依赖冲突
   - 如果有冲突，会给出明确提示

4. **兼容性**
   - 可以同时保留 requirements.txt（用于 Docker 等场景）
   - 使用 `poetry export` 定期更新 requirements.txt

## 🐛 常见问题

### Q: Poetry 安装很慢？
A: 配置国内镜像源（见上面配置部分）

### Q: 如何在 Docker 中使用？
A: 
```dockerfile
FROM python:3.10
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false
RUN poetry install --no-dev
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Q: 如何回到 pip？
A: 
```bash
poetry export -f requirements.txt --output requirements.txt
pip install -r requirements.txt
```

## 📚 更多资源

- 官方文档: https://python-poetry.org/docs/
- 中文文档: https://python-poetry.org/docs/zh/
- GitHub: https://github.com/python-poetry/poetry

