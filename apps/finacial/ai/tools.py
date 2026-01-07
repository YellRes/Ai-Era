"""
财务分析工具集
包含各种财务分析相关的工具函数
"""

import os
import re
from langchain_core.tools import tool
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# 全局变量：存储加载的PDF向量数据库
pdf_vectorstore = None
pdf_content = None


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
            chunk_size=800,  # 适当增大，保证财务表格完整性
            chunk_overlap=200,  # 增加重叠，避免关键信息被切断
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
                model_name="BAAI/bge-base-zh-v1.5",  # 专门的中文 Embedding 模型，约400MB
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


def expand_query_with_synonyms(query: str, max_expansion: int = 3) -> list:
    """
    扩展查询词，增加财务领域同义词/相关词（精简版）
    
    Args:
        query: 原始查询词
        max_expansion: 最大扩展词数量（默认3个，避免搜索过多）
    
    Returns:
        扩展后的查询词列表
    """
    # 财务领域同义词映射（精简版，只保留最常用的变体）
    financial_synonyms = {
        "利润": ["净利润", "归属于母公司股东的净利润"],
        "收入": ["营业收入", "营业总收入"],
        "资产": ["总资产", "资产总计"],
        "负债": ["总负债", "负债合计"],
        "现金流": ["经营活动产生的现金流量净额"],
        "毛利": ["毛利率"],
        "净利率": ["销售净利率"],
        "ROE": ["净资产收益率"],
        "ROA": ["总资产收益率"],
        "EPS": ["每股收益", "基本每股收益"],
        "营收": ["营业收入"],
        "成本": ["营业成本"],
        "费用": ["销售费用", "管理费用", "财务费用"],
    }
    
    queries = [query]
    
    # 只匹配第一个命中的关键词，避免过度扩展
    for key, synonyms in financial_synonyms.items():
        if key in query:
            # 只添加有限数量的同义词
            queries.extend(synonyms[:max_expansion])
            break
        for syn in synonyms:
            if syn in query:
                queries.append(key)
                break
    
    # 去重并返回，限制总数量
    unique_queries = list(set(queries))
    return unique_queries[:max_expansion + 1]  # 原始查询 + max_expansion 个扩展词


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
        # 扩展查询词
        expanded_queries = expand_query_with_synonyms(query)
        
        all_docs = []
        seen_contents = set()
        
        # 对每个查询词进行检索
        for q in expanded_queries:
            # 使用带分数的相似性搜索，获取更多候选
            docs_with_scores = pdf_vectorstore.similarity_search_with_score(q, k=5)
            
            for doc, score in docs_with_scores:
                # 过滤低相关度结果（分数越低越相似，FAISS 使用 L2 距离）
                # 同时去重
                content_hash = hash(doc.page_content[:100])
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    all_docs.append((doc, score, q))
        
        if not all_docs:
            return f"未找到关于'{query}'的相关信息"
        
        # 按相似度分数排序（分数越低越好）
        all_docs.sort(key=lambda x: x[1])
        
        # 取前5个最相关的结果
        top_docs = all_docs[:5]
        
        # 整合检索结果
        result = f"📄 关于'{query}'的相关信息：\n\n"
        for i, (doc, score, matched_query) in enumerate(top_docs, 1):
            result += f"片段 {i} (匹配词: {matched_query}, 相关度: {1/(1+score):.2%}):\n{doc.page_content}\n\n{'='*50}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ 检索失败: {str(e)}"


def extract_number_from_text(text: str) -> list:
    """
    从文本中提取所有数字（支持千分位、小数、负数、带单位）
    
    Returns:
        [(数字值, 原始字符串), ...]
    """
    # 匹配各种数字格式：负数、千分位、小数、带单位（万、亿、元）
    patterns = [
        r'(-?[\d,，]+\.?\d*)\s*(?:万元|亿元|元)?',
        r'(-?[\d,，]+\.?\d*)',
    ]
    
    results = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            # 清理格式
            clean_num = match.replace(',', '').replace('，', '').strip()
            if clean_num and clean_num not in ['-', '.']:
                try:
                    value = float(clean_num)
                    if abs(value) > 0:  # 排除0
                        results.append((value, match))
                except:
                    pass
    
    # 去重
    seen = set()
    unique_results = []
    for value, original in results:
        if value not in seen:
            seen.add(value)
            unique_results.append((value, original))
    
    return unique_results


@tool
def extract_financial_data(data_type: str) -> str:
    """
    从PDF中提取特定的财务数据（通过 RAG 检索 + 智能匹配）
    
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
        提取的财务数据及相关上下文
    """
    global pdf_vectorstore, pdf_content
    
    if pdf_vectorstore is None:
        return "❌ 请先使用 load_financial_pdf 工具加载PDF文件"
    
    # 财务指标的检索关键词和别名
    data_config = {
        'revenue': {
            'name': '营业收入',
            'keywords': ['营业收入', '营业总收入', '主营业务收入', '一、营业收入'],
            'patterns': [
                r'(?:一、)?营业(?:总)?收入[^\d]*?([\d,，]+(?:\.\d+)?)',
                r'营业收入\s+([\d,，]+(?:\.\d+)?)',
            ]
        },
        'net_income': {
            'name': '净利润',
            'keywords': ['净利润', '归属于母公司所有者的净利润', '归属于上市公司股东的净利润'],
            'patterns': [
                r'(?:四、)?净利润[^\d]*?([\d,，-]+(?:\.\d+)?)',
                r'归属于.*?净利润[^\d]*?([\d,，-]+(?:\.\d+)?)',
            ]
        },
        'total_assets': {
            'name': '总资产',
            'keywords': ['资产总计', '资产总额', '总资产'],
            'patterns': [
                r'资产总计[^\d]*?([\d,，]+(?:\.\d+)?)',
                r'总资产[^\d]*?([\d,，]+(?:\.\d+)?)',
            ]
        },
        'total_liabilities': {
            'name': '总负债',
            'keywords': ['负债合计', '负债总计', '负债总额'],
            'patterns': [
                r'负债(?:合计|总计)[^\d]*?([\d,，]+(?:\.\d+)?)',
            ]
        },
        'equity': {
            'name': '股东权益',
            'keywords': ['所有者权益合计', '股东权益合计', '归属于母公司所有者权益'],
            'patterns': [
                r'(?:所有者|股东)权益.*?合计[^\d]*?([\d,，]+(?:\.\d+)?)',
                r'归属于母公司.*?权益[^\d]*?([\d,，]+(?:\.\d+)?)',
            ]
        },
        'current_assets': {
            'name': '流动资产',
            'keywords': ['流动资产合计', '流动资产小计'],
            'patterns': [
                r'流动资产(?:合计|小计)[^\d]*?([\d,，]+(?:\.\d+)?)',
            ]
        },
        'current_liabilities': {
            'name': '流动负债',
            'keywords': ['流动负债合计', '流动负债小计'],
            'patterns': [
                r'流动负债(?:合计|小计)[^\d]*?([\d,，]+(?:\.\d+)?)',
            ]
        },
        'cash': {
            'name': '货币资金',
            'keywords': ['货币资金', '现金及现金等价物', '库存现金'],
            'patterns': [
                r'货币资金[^\d]*?([\d,，]+(?:\.\d+)?)',
                r'现金及现金等价物[^\d]*?([\d,，]+(?:\.\d+)?)',
            ]
        },
        'operating_income': {
            'name': '归属于上市公司股东的扣除非经常性损益的净利润',
            'keywords': ['扣除非经常性损益', '扣非净利润', '扣除非经常性损益的净利润'],
            'patterns': [
                r'扣除非经常性损益.*?净利润[^\d]*?([\d,，-]+(?:\.\d+)?)',
                r'归属于上市公司股东的扣除非经常性损益的净利润[^\d]*?([\d,，-]+(?:\.\d+)?)',
            ]
        },
    }
    
    def search_and_extract(config):
        """使用 RAG 检索并提取数据"""
        all_context = []
        extracted_values = []
        
        # 对每个关键词进行检索
        for keyword in config['keywords']:
            try:
                docs = pdf_vectorstore.similarity_search(keyword, k=3)
                for doc in docs:
                    content = doc.page_content
                    all_context.append(content)
                    
                    # 尝试用正则提取数值
                    for pattern in config['patterns']:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            clean_num = match.replace(',', '').replace('，', '').strip()
                            try:
                                value = float(clean_num)
                                if abs(value) > 0:
                                    extracted_values.append(value)
                            except:
                                pass
            except:
                pass
        
        # 返回找到的值（取最大值，通常财务报表的合计数较大）
        unique_values = list(set(extracted_values))
        unique_values.sort(reverse=True)
        
        return unique_values, all_context
    
    if data_type == 'all':
        # 提取所有指标
        result = "📊 提取的财务数据：\n\n"
        extracted_data = {}
        
        for key, config in data_config.items():
            values, contexts = search_and_extract(config)
            if values:
                # 取最可能的值（通常是最大的）
                value = values[0]
                extracted_data[key] = value
                result += f"- {config['name']}: {value:,.2f}\n"
            else:
                result += f"- {config['name']}: 未找到\n"
        
        # 如果提取到数据较少，附加原始上下文供 LLM 分析
        found_count = len([v for v in extracted_data.values() if v])
        if found_count < 5:
            result += "\n\n⚠️ 部分数据未能自动提取，以下是相关原始内容供分析：\n\n"
            # 检索主要财务报表区域
            for keyword in ['利润表', '资产负债表', '主要会计数据']:
                try:
                    docs = pdf_vectorstore.similarity_search(keyword, k=2)
                    for doc in docs:
                        result += f"---\n{doc.page_content[:500]}\n"
                except:
                    pass
        
        return result
    
    elif data_type in data_config:
        config = data_config[data_type]
        values, contexts = search_and_extract(config)
        
        if values:
            result = f"📊 {config['name']}: {values[0]:,.2f}\n"
            if len(values) > 1:
                result += f"   (其他候选值: {', '.join([f'{v:,.2f}' for v in values[1:3]])})\n"
            result += f"\n相关上下文:\n{contexts[0][:300] if contexts else '无'}..."
            return result
        else:
            # 返回检索到的原始内容，让 LLM 自行分析
            result = f"❓ 未能自动提取 {config['name']}，以下是相关内容：\n\n"
            for keyword in config['keywords'][:2]:
                try:
                    docs = pdf_vectorstore.similarity_search(keyword, k=2)
                    for doc in docs:
                        result += f"---\n{doc.page_content[:400]}\n"
                except:
                    pass
            return result
    
    else:
        return f"不支持的数据类型: {data_type}"


# 导出所有工具
__all__ = [
    'calculate_financial_ratio',
    'analyze_profitability',
    'analyze_liquidity',
    'analyze_leverage',
    'load_financial_pdf',
    'search_financial_info',
    'extract_financial_data',
    'expand_query_with_synonyms',
    'extract_number_from_text',
    'pdf_vectorstore',
    'pdf_content',
]
