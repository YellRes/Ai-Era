"""
财务报表分析智能体
基于 LangChain 和 DeepSeek 创建的智能财务分析助手
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import Optional, Generator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 禁用 httpx 的 HTTP 请求日志
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

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

# 全局变量：存储加载的PDF向量数据库
pdf_vectorstore = None
pdf_content = None


# 定义财务分析工具
@tool
def calculate_financial_ratio(metric: str, numerator: float, denominator: float) -> str:
    """
    计算财务比率
    
    Args:
        metric: 比率名称（如 'ROE', 'ROA', 'current_ratio', 'debt_ratio'）
        numerator: 分子
        denominator: 分母
    
    Returns:
        计算结果的描述
    """
    if denominator == 0:
        return f"错误：分母不能为零"
    
    ratio = numerator / denominator
    
    metric_names = {
        'ROE': '净资产收益率',
        'ROA': '总资产收益率',
        'current_ratio': '流动比率',
        'debt_ratio': '资产负债率',
        'profit_margin': '利润率'
    }
    
    metric_name = metric_names.get(metric, metric)
    
    if metric in ['ROE', 'ROA', 'profit_margin', 'debt_ratio']:
        percentage = ratio * 100
        return f"{metric_name}: {percentage:.2f}%"
    else:
        return f"{metric_name}: {ratio:.2f}"


@tool
def analyze_profitability(revenue: float, net_income: float, total_assets: float, operating_income: float) -> str:
    """
    分析企业盈利能力
    
    Args:
        revenue: 营业收入
        net_income: 净利润
        total_assets: 总资产
        operating_income: 归属于上市公司股东的扣除非经常性损益的净利润
    
    Returns:
        盈利能力分析报告
    """
    if revenue == 0 or total_assets == 0:
        return "错误：收入或总资产不能为零"
    
    profit_margin = (net_income / revenue) * 100
    roa = (net_income / total_assets) * 100
    operating_profit_margin = (operating_income / revenue) * 100
    analysis = f"""
📊 盈利能力分析报告：
- 利润率: {profit_margin:.2f}%
- 总资产收益率(ROA): {roa:.2f}%
- 归属于上市公司股东的扣除非经常性损益的净利润率: {operating_profit_margin:.2f}%

💡 分析结论：
"""
    
    if profit_margin > 15:
        analysis += "- 利润率表现优秀，盈利能力强\n"
    elif profit_margin > 5:
        analysis += "- 利润率处于合理水平\n"
    else:
        analysis += "- 利润率偏低，需要关注成本控制\n"
    
    if roa > 10:
        analysis += "- 资产使用效率高，投资回报良好\n"
    elif roa > 5:
        analysis += "- 资产使用效率中等\n"
    else:
        analysis += "- 资产使用效率较低，需要优化资产配置\n"
    
    return analysis + "归属于上市公司股东的扣除非经常性损益的净利润率: {operating_profit_margin:.2f}%"


@tool
def analyze_liquidity(current_assets: float, current_liabilities: float, 
                      cash: float, inventory: float) -> str:
    """
    分析企业流动性和偿债能力
    
    Args:
        current_assets: 流动资产
        current_liabilities: 流动负债
        cash: 现金及现金等价物
        inventory: 存货
    
    Returns:
        流动性分析报告
    """
    if current_liabilities == 0:
        return "错误：流动负债不能为零"
    
    current_ratio = current_assets / current_liabilities
    quick_ratio = (current_assets - inventory) / current_liabilities
    cash_ratio = cash / current_liabilities
    
    analysis = f"""
💰 流动性分析报告：
- 流动比率: {current_ratio:.2f}
- 速动比率: {quick_ratio:.2f}
- 现金比率: {cash_ratio:.2f}

💡 分析结论：
"""
    
    if current_ratio >= 2:
        analysis += "- 流动比率健康，短期偿债能力强\n"
    elif current_ratio >= 1:
        analysis += "- 流动比率基本合理\n"
    else:
        analysis += "- 流动比率偏低，存在短期偿债风险\n"
    
    if quick_ratio >= 1:
        analysis += "- 速动比率良好，变现能力强\n"
    else:
        analysis += "- 速动比率偏低，需要关注存货周转\n"
    
    return analysis


@tool
def analyze_leverage(total_assets: float, total_liabilities: float, 
                     equity: float, interest_expense: float, ebit: float) -> str:
    """
    分析企业杠杆和资本结构
    
    Args:
        total_assets: 总资产
        total_liabilities: 总负债
        equity: 股东权益
        interest_expense: 利息费用
        ebit: 息税前利润
    
    Returns:
        杠杆分析报告
    """
    if total_assets == 0 or equity == 0:
        return "错误：总资产或股东权益不能为零"
    
    debt_ratio = (total_liabilities / total_assets) * 100
    equity_ratio = (equity / total_assets) * 100
    debt_to_equity = total_liabilities / equity if equity != 0 else 0
    
    analysis = f"""
🏦 杠杆与资本结构分析：
- 资产负债率: {debt_ratio:.2f}%
- 股东权益比率: {equity_ratio:.2f}%
- 负债权益比: {debt_to_equity:.2f}

💡 分析结论：
"""
    
    if debt_ratio < 40:
        analysis += "- 负债水平较低，财务风险小\n"
    elif debt_ratio < 60:
        analysis += "- 负债水平适中，资本结构合理\n"
    else:
        analysis += "- 负债水平较高，需要关注财务风险\n"
    
    if interest_expense > 0 and ebit > 0:
        interest_coverage = ebit / interest_expense
        analysis += f"- 利息保障倍数: {interest_coverage:.2f}倍\n"
        if interest_coverage > 5:
            analysis += "  → 利息偿付能力强\n"
        elif interest_coverage > 2:
            analysis += "  → 利息偿付能力尚可\n"
        else:
            analysis += "  → 利息偿付压力较大\n"
    
    return analysis


@tool
def load_financial_pdf(pdf_path: str) -> str:
    """
    加载并处理财务报表PDF文件（中文优化版）
    
    Args:
        pdf_path: PDF文件的路径
    
    Returns:
        加载状态信息
    """
    global pdf_vectorstore, pdf_content
    
    try:
        # 使用 PyMuPDF 加载PDF（对中文支持更好）
        print("📂 正在加载PDF文件...")
        # load_fn = PyMuPDFLoader if is_online else OnlinePDFLoader
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        print(f"✓ 已加载 {len(documents)} 页")
        
        # 保存原始内容
        pdf_content = "\n\n".join([doc.page_content for doc in documents])
        
        # 中文优化的文本分割
        print("📝 正在分割文本...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # 中文字符密度大，适当减小
            chunk_overlap=100,
            separators=[
                "\n\n",    # 段落
                "\n",      # 换行
                "。",      # 中文句号
                "！",      # 中文感叹号
                "？",      # 中文问号
                "；",      # 中文分号（财务报表常用）
                "，",      # 中文逗号
                ".",       # 英文句号
                "!",       # 英文感叹号
                "?",       # 英文问号
                " ",       # 空格
                ""         # 字符级别
            ],
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        print(f"✓ 已分割为 {len(splits)} 个文本块")
        
        # 使用本地中文 Embedding 模型创建向量存储
        try:
            print("🔧 正在加载中文 Embedding 模型（首次运行会自动下载）...")
            embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-base-zh-v1.5",  # 专门的中文 Embedding 模型
                model_kwargs={'device': 'cpu'},  # 使用 CPU，如有 GPU 可改为 'cuda'
                encode_kwargs={'normalize_embeddings': True}
            )
            
            print("🔍 正在创建向量索引...")
            pdf_vectorstore = FAISS.from_documents(splits, embeddings)
            print("✓ 向量索引创建完成")
            
            return f"""✅ 成功加载中文PDF文件！
📊 文档信息：
  - 文档页数: {len(documents)}
  - 文本块数: {len(splits)}
  - Embedding模型: BAAI/bge-base-zh-v1.5（中文优化）
  - 向量数据库: FAISS
  
✨ 已建立向量索引，可以开始查询分析财务数据！"""
            
        except Exception as emb_error:
            return f"""❌ 创建向量索引失败: {str(emb_error)}

💡 解决方案：
1. 请确保已安装依赖：pip install sentence-transformers
2. 首次运行会自动下载模型（约400MB），请确保网络连接正常
3. 如果下载失败，可以尝试手动设置镜像源或使用代理"""
    
    except Exception as e:
        return f"❌ 加载PDF文件失败: {str(e)}\n\n💡 提示：请确保PDF文件路径正确，且文件未损坏。"


@tool
def search_financial_info(query: str) -> str:
    """
    从已加载的财务报表PDF中检索相关信息
    
    Args:
        query: 要查询的财务信息（如"营业收入"、"净利润"、"资产负债表"、"归属于上市公司股东的扣除非经常性损益的净利润"等）
    
    Returns:
        检索到的相关信息
    """
    global pdf_vectorstore
    
    if pdf_vectorstore is None:
        return "❌ 请先使用 load_financial_pdf 工具加载PDF文件"
    
    try:
        # 检索相关文档
        docs = pdf_vectorstore.similarity_search(query, k=3)
        
        if not docs:
            return f"未找到关于'{query}'的相关信息"
        
        # 整合检索结果
        result = f"📄 关于'{query}'的相关信息：\n\n"
        for i, doc in enumerate(docs, 1):
            result += f"片段 {i}:\n{doc.page_content}\n\n{'='*50}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ 检索失败: {str(e)}"


@tool
def extract_financial_data(data_type: str) -> str:
    """
    从PDF中提取特定的财务数据
    
    Args:
        data_type: 数据类型，可选值包括：
            - 'revenue': 营业收入
            - 'net_income': 净利润  
            - 'total_assets': 总资产
            - 'total_liabilities': 总负债
            - 'equity': 股东权益
            - 'current_assets': 流动资产
            - 'current_liabilities': 流动负债
            - 'cash': 现金及现金等价物
            - 'operating_income': 归属于上市公司股东的扣除非经常性损益的净利润
            - 'all': 提取所有关键财务指标
    
    Returns:
        提取的财务数据
    """
    global pdf_content
    
    if pdf_content is None:
        return "❌ 请先使用 load_financial_pdf 工具加载PDF文件"
    
    # 定义财务指标的匹配模式
    patterns = {
        'revenue': [
            r'营业收入[：:]\s*([\d,，.]+)',
            r'营业总收入[：:]\s*([\d,，.]+)',
            r'一、营业总收入\s+([\d,，.]+)',
        ],
        'net_income': [
            r'净利润[：:]\s*([\d,，.]+)',
            r'归属于.*净利润[：:]\s*([\d,，.]+)',
            r'四、净利润.*\s+([\d,，.]+)',
        ],
        'total_assets': [
            r'资产总计[：:]\s*([\d,，.]+)',
            r'总资产[：:]\s*([\d,，.]+)',
        ],
        'total_liabilities': [
            r'负债合计[：:]\s*([\d,，.]+)',
            r'负债总计[：:]\s*([\d,，.]+)',
        ],
        'equity': [
            r'所有者权益.*合计[：:]\s*([\d,，.]+)',
            r'股东权益合计[：:]\s*([\d,，.]+)',
        ],
        'current_assets': [
            r'流动资产合计[：:]\s*([\d,，.]+)',
        ],
        'current_liabilities': [
            r'流动负债合计[：:]\s*([\d,，.]+)',
        ],
        'cash': [
            r'货币资金[：:]\s*([\d,，.]+)',
            r'现金及现金等价物[：:]\s*([\d,，.]+)',
        ],
        'operating_income': [
            r'归属于上市公司股东的扣除非经常性损益的净利润[：:]\s*([\d,，.]+)',
            r'非经常性损益净利润[：:]\s*([\d,，.]+)',
        ],
    }
    
    def extract_number(text, pattern_list):
        """从文本中提取数字"""
        for pattern in pattern_list:
            matches = re.findall(pattern, text)
            if matches:
                # 清理数字格式
                number_str = matches[0].replace(',', '').replace('，', '')
                try:
                    return float(number_str)
                except:
                    continue
        return None
    
    if data_type == 'all':
        # 提取所有指标
        result = "📊 提取的财务数据：\n\n"
        data_names = {
            'operating_income': '归属于上市公司股东的扣除非经常性损益的净利润',
            'revenue': '营业收入',
            'net_income': '净利润',
            'total_assets': '总资产',
            'total_liabilities': '总负债',
            'equity': '股东权益',
            'current_assets': '流动资产',
            'current_liabilities': '流动负债',
            'cash': '货币资金',
        }
        
        for key, name in data_names.items():
            value = extract_number(pdf_content, patterns.get(key, []))
            if value:
                result += f"- {name}: {value:,.2f}\n"
        
        return result
    
    elif data_type in patterns:
        value = extract_number(pdf_content, patterns[data_type])
        if value:
            data_names = {
                'operating_income': '归属于上市公司股东的扣除非经常性损益的净利润',
                'revenue': '营业收入',
                'net_income': '净利润',
                'total_assets': '总资产',
                'total_liabilities': '总负债',
                'equity': '股东权益',
                'current_assets': '流动资产',
                'current_liabilities': '流动负债',
                'cash': '货币资金',
            }
            return f"{data_names[data_type]}: {value:,.2f}"
        else:
            return f"未能从PDF中提取到'{data_type}'相关数据"
    
    else:
        return f"不支持的数据类型: {data_type}"


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
        search_financial_info,
        extract_financial_data,
        calculate_financial_ratio,
        analyze_profitability,
        analyze_liquidity,
        analyze_leverage,
    ]
    
    # 创建内存保存器
    memory = MemorySaver()
    
    # 创建系统提示（使用 SystemMessage 对象）
    system_message = SystemMessage(content="""你是一位专业的财务分析师助手，擅长分析企业财务报表。

你的职责包括：
1. 加载和读取PDF格式的财务报表
2. 从财务报表中提取关键财务数据
3. 计算各种财务比率（如 ROE、ROA、流动比率等）
4. 分析企业的盈利能力
5. 评估企业的流动性和偿债能力
6. 分析企业的杠杆和资本结构
7. 提供专业的财务建议
8. 提供真实客观的分析，不能故意说好话

可用工具说明：
- load_financial_pdf: 加载PDF财务报表文件
- search_financial_info: 从PDF中检索特定信息
- extract_financial_data: 自动提取财务数据（营业收入、净利润等）
- calculate_financial_ratio: 计算财务比率
- analyze_profitability: 分析盈利能力
- analyze_liquidity: 分析流动性
- analyze_leverage: 分析杠杆

工作流程：
1. 当用户提供PDF文件路径时，首先使用 load_financial_pdf 加载文件
2. 仅当用户明确要求时，才使用 extract_financial_data 提取数据或使用分析工具
3. 完成用户要求的具体任务后，立即给出结论，不要进行额外的分析

⚠️ 重要规则：
- 只执行用户明确要求的任务
- 如果用户只要求"加载PDF"，加载完成后就停止，不要自动分析
- 如果用户只要求"提取数据"，提取完成后就停止
- 避免过度使用工具，每个任务只调用必要的工具
- 使用中文回答

如果用户提供了财务数据或PDF文件，请根据用户的具体要求使用相应的工具。""")
    
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
        f"请加载这个PDF文件：{pdf_path}",
        "从PDF中提取所有关键财务数据",
        "基于提取的数据，分析这家公司的整体财务状况",
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
        f"请加载这个PDF文件：{pdf_path}",
        "从PDF中提取所有关键财务数据",
        "基于提取的数据，分析这家公司的整体财务状况",
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
        stream = agent.stream(
            {"messages": messages},
            config=config,
            stream_mode="values"
        )
        
        # 使用生成器逐个产生事件
        for chunk in stream:
            latest_message = chunk["messages"][-1]
            
            if latest_message.content:
                yield {
                    "type": "message",
                    "step": i,
                    "content": latest_message.content
                }
            elif hasattr(latest_message, 'tool_calls') and latest_message.tool_calls:
                tools = [tc['name'] for tc in latest_message.tool_calls]
                yield {
                    "type": "tool_call",
                    "step": i,
                    "tools": tools
                }
    
    # 分析完成
    yield {
        "type": "complete",
        "message": "分析完成"
    }

if __name__ == "__main__":
    pdf_path = "pdf/000001.pdf"
    print(main(pdf_path))