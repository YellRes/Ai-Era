---
target_file: apps/finacial/ai/index.py
created_at: 2026-01-09
tags: [analysis, langgraph, financial-agent, python]
---

# apps/finacial/ai/index.py 分析

## 概览

该文件是用 Python 编写的财务报表分析智能体（Agent）的入口文件。
它基于 **LangChain** 和 **LangGraph** 框架构建，利用 **DeepSeek** 大模型（通过 OpenAI 兼容接口）来执行财务分析任务。

## 核心功能

1.  **AI 智能体构建**: 创建一个基于 React 模式的 Agent，具备调用工具的能力。
2.  **工具集成**: 集成了 PDF 加载、数据提取、财务比率计算等多种工具。
3.  **流式响应**: 提供了支持流式输出（Server-Sent Events 风格）的执行函数，适配前端实时显示。

## 代码结构

### 1. 初始化与配置

- **环境**: 加载 `.dotenv`，配置 `DEEPSEEK_API_KEY`。
- **日志**: 禁用了 `httpx` 的冗余日志。
- **平台兼容**: 针对 Windows 调整了控制台编码为 UTF-8。

### 2. `create_financial_agent()`

- **LLM**: 初始化 `ChatOpenAI`，指向 DeepSeek API (`https://api.deepseek.com`)。
- **Tools**: 注册了一系列财务分析工具：
  - `load_financial_pdf`: 加载 PDF。
  - `extract_financial_metrics`: 提取数据。
  - `calculate_financial_ratio`: 计算比率。
  - `analyze_profitability/liquidity/leverage`: 专项分析工具。
- **System Prompt**: 加载 `FINANCIAL_ANALYST_PROMPT` 作为系统人设。
- **Memory**: 使用 `MemorySaver` 实现简易的会话记忆。
- **Return**: 返回编译好的 `agent` (LangGraph CompiledGraph) 和 `system_message`。

### 3. `main_with_pdf(pdf_path)` (核心业务入口)

- 这是一个生成器函数 (`Generator`)，用于流式返回分析结果。
- **流程**:
  1.  初始化 Agent。
  2.  调用 `agent.stream(..., stream_mode="messages")`。
  3.  **事件转换**: 将 LangGraph 的原始事件转换为前端友好的 JSON 格式：
      - `message`: AI 的文本回复。
      - `tool_call`: 工具调用开始。
      - `tool_call_chunk`: 工具调用的流式输出。
      - `complete`: 结束信号。

### 4. `main(pdf_path)`

- 旧版/调试用的非流式或简单流式入口，主要用于本地直接运行测试。

## 依赖关系

- **外部库**: `langchain_openai`, `langgraph`, `dotenv`
- **内部模块**:
  - `.tools`: 具体工具实现的集合。
  - `.prompts`: 提示词文件。

## 下一步建议

- 当前 `main` 和 `main_with_pdf` 有一定逻辑重复，未来可考虑统一。
- 错误处理较少，特别是 API 调用失败或 PDF 解析失败的情况。
