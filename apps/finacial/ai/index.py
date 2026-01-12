"""
财务报表分析智能体
基于 LangChain 和 DeepSeek 创建的智能财务分析助手
"""

import os
import sys
import logging
from typing import Generator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 禁用 httpx 的 HTTP 请求日志
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# 导入工具
from .tools import (
    load_financial_pdf,
    extract_financial_metrics,
    calculate_financial_ratio,
    analyze_profitability,
    analyze_liquidity,
    analyze_leverage,
    analyze_qualitative_content,
)

# 导入提示词
from .prompts import FINANCIAL_ANALYST_PROMPT

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PDF 保存目录（相对于脚本位置的上级目录中的 pdf 文件夹）
PDF_DIR = os.path.join(SCRIPT_DIR, '..', 'pdf')


# 设置控制台编码为 UTF-8（修复 Windows 下的编码问题）
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 加载环境变量
load_dotenv()

# 检查 API 密钥
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print("⚠️  警告：未找到 DEEPSEEK_API_KEY 环境变量")
    print("请在项目目录下创建 .env 文件并添加：")
    print("DEEPSEEK_API_KEY=your_api_key_here\n")


def create_financial_agent():
    """创建财务分析智能体"""
    
    # 初始化 DeepSeek 模型
    # 说明：DeepSeek 提供 OpenAI 兼容的 API，所以使用 ChatOpenAI 类
    # 只需将 openai_api_base 设置为 DeepSeek 的 API 地址即可
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=DEEPSEEK_API_KEY,  # 使用 DeepSeek API Key
        openai_api_base="https://api.deepseek.com",  # DeepSeek API 地址
        temperature=0,
    )
    
    # 定义工具列表
    tools = [
        load_financial_pdf,
        extract_financial_metrics,
        calculate_financial_ratio,
        analyze_profitability,
        analyze_liquidity,
        analyze_leverage,
        analyze_qualitative_content,
    ]
    
    # 创建内存保存器
    memory = MemorySaver()
    
    # 创建系统提示（使用 SystemMessage 对象）
    system_message = SystemMessage(content=FINANCIAL_ANALYST_PROMPT)
    
    # 创建 ReAct agent
    agent = create_react_agent(llm, tools, checkpointer=memory)
    
    return agent, system_message


def main(pdf_path):
    """运行带PDF分析的示例 - 流式版本"""
    print("="*60)
    print("🏢 财务报表PDF分析示例")
    print("="*60)
    
    # 创建 agent
    agent, system_message = create_financial_agent()
    
    # 测试查询
    test_queries = [
        f"请加载这个PDF文件：{pdf_path},分析这家公司的整体财务状况",
    ]
    
    thread_id = "pdf_analysis_session"
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 100000
    }
    
    for i, query in enumerate(test_queries, 1):
        # 第一次对话时包含系统消息
        if i == 1:
            messages = [system_message, HumanMessage(content=query)]
        else:
            messages = [HumanMessage(content=query)]

        # 返回流
        stream = agent.invoke(
            {"messages": messages},
            config=config
        )
        return stream.content
  


def main_with_pdf(pdf_path: str) -> Generator:
    """运行带PDF分析的示例 - 流式版本"""
    print("="*60)
    print("🏢 财务报表PDF分析示例")
    print("="*60)
    
    # 创建 agent
    agent, system_message = create_financial_agent()
    
    # 测试查询
    test_queries = [
        f"请加载这个PDF文件：{pdf_path}, 从PDF中提取所有关键财务数据, 基于提取的数据，分析这家公司的整体财务状况"
    ]
    
    thread_id = "pdf_analysis_session"
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 100000
    }
    
    for i, query in enumerate(test_queries, 1):
        # 第一次对话时包含系统消息
        if i == 1:
            messages = [system_message, HumanMessage(content=query)]
        else:
            messages = [HumanMessage(content=query)]

        # 返回流 (messages 模式返回 (message, metadata) 元组)
        stream = agent.stream(
            {"messages": messages},
            config=config,
            stream_mode="messages"
        )
        
        # 使用生成器逐个产生事件
        for message, metadata in stream:
            # messages 模式下，message 是 AIMessageChunk 或其他消息类型
            # metadata 包含 langgraph_node 等信息
            
            # 处理 AI 消息内容（流式文本）
            if hasattr(message, 'content') and message.content:
                yield {
                    "type": "message",
                    "step": i,
                    "content": message.content,
                    "node": metadata.get("langgraph_node", "unknown")
                }
            
            # 处理工具调用
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tools = [tc['name'] for tc in message.tool_calls]
                yield {
                    "type": "tool_call",
                    "step": i,
                    "tools": tools,
                    "node": metadata.get("langgraph_node", "unknown")
                }
            
            # 处理工具调用块（流式工具调用）
            if hasattr(message, 'tool_call_chunks') and message.tool_call_chunks:
                for chunk in message.tool_call_chunks:
                    yield {
                        "type": "tool_call_chunk",
                        "step": i,
                        "name": chunk.get("name", ""),
                        "args": chunk.get("args", ""),
                        "node": metadata.get("langgraph_node", "unknown")
                    }
    
    # 分析完成
    yield {
        "type": "complete",
        "message": "分析完成"
    }

if __name__ == "__main__":
    pdf_path = "pdf/000001.pdf"
    print(main(pdf_path))