"""
PDF 数据加载工具集
包含 PDF 文件加载、解析和数据提取相关的工具函数
"""

import os
import re
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# 全局变量：存储加载的PDF向量数据库
pdf_vectorstore = None
pdf_content = None


def extract_financial_metrics(documents: list) -> dict:
    """
    从 PDF 文档中提取关键财务指标
    
    Args:
        documents: PyMuPDFLoader 加载的文档列表
    
    Returns:
        包含财务指标的字典
    """
    # 合并所有页面内容
    full_text = "\n".join([doc.page_content for doc in documents])
    
    metrics = {}
    
    # 定义要提取的财务指标及其正则模式
    # 格式：指标名称 -> (正则模式, 数值组索引)
    patterns = {
        # 利润表指标 (每个汉字之间都允许空白符,最大化兼容性)
        "营业收入": r"营[\s\n]*业[\s\n]*(?:总[\s\n]*)?收[\s\n]*入[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*([\d,，]+\.?\d*)",
        "利润总额": r"利[\s\n]*润[\s\n]*总[\s\n]*额[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*([\d,，]+\.?\d*)",
        "归属于上市公司股东的净利润": r"归[\s\n]*属[\s\n]*于[\s\n]*上[\s\n]*市[\s\n]*公[\s\n]*司[\s\n]*股[\s\n]*东[\s\n]*的?[\s\n]*净[\s\n]*利[\s\n]*润[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*(-?[\d,，]+\.?\d*)",
        "扣非净利润": r"扣[\s\n]*除[\s\n]*非?[\s\n]*经[\s\n]*常[\s\n]*性[\s\n]*损[\s\n]*益[\s\n]*的?[\s\n]*净[\s\n]*利[\s\n]*润[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*(-?[\d,，]+\.?\d*)",
        
        # 每股指标
        "基本每股收益": r"基[\s\n]*本[\s\n]*每[\s\n]*股[\s\n]*收[\s\n]*益[（(]?元/股[)）]?[\s\n|｜]*(?:—[\s\n]*)*(-?[\d.]+)",
        "稀释每股收益": r"稀[\s\n]*释[\s\n]*每[\s\n]*股[\s\n]*收[\s\n]*益[（(]?元/股[)）]?[\s\n|｜]*(?:—[\s\n]*)*(-?[\d.]+)",
        
        # 资产负债表指标
        "总资产": r"总[\s\n]*资[\s\n]*产[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*([\d,，]+\.?\d*)",
        "归属于上市公司股东的所有者权益": r"归[\s\n]*属[\s\n]*于[\s\n]*上[\s\n]*市[\s\n]*公[\s\n]*司[\s\n]*股[\s\n]*东[\s\n]*的?[\s\n]*所[\s\n]*有[\s\n]*者[\s\n]*权[\s\n]*益[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*([\d,，]+\.?\d*)",
        
        # 现金流指标
        "经营活动产生的现金流量净额": r"经[\s\n]*营[\s\n]*活[\s\n]*动[\s\n]*产[\s\n]*生[\s\n]*的[\s\n]*现[\s\n]*金[\s\n]*流[\s\n]*量[\s\n]*净[\s\n]*额[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*(-?[\d,，]+\.?\d*)",
        
        # 收益率指标
        "加权平均净资产收益率": r"加[\s\n]*权[\s\n]*平[\s\n]*均[\s\n]*净[\s\n]*资[\s\n]*产[\s\n]*收[\s\n]*益[\s\n]*率[（(]?%?[)）]?[\s\n|｜]*(?:—[\s\n]*)*(-?[\d.]+)%?",
    }
    
    for metric_name, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            value_str = match.group(1)
            # 清理数值：移除逗号，转换为浮点数
            value_str = value_str.replace(",", "").replace("，", "")
            try:
                metrics[metric_name] = float(value_str)
            except ValueError:
                metrics[metric_name] = value_str
    
    return metrics


def extract_financial_table(page_content: str) -> list:
    """
    从单页内容中提取表格数据
    
    Args:
        page_content: 单页的文本内容
    
    Returns:
        表格行数据列表
    """
    rows = []
    lines = page_content.split('\n')
    
    for line in lines:
        # 匹配包含数字的行（可能是表格数据）
        # 财务报表中的数据行通常包含多个数字
        numbers = re.findall(r'-?[\d,，]+\.?\d*', line)
        if len(numbers) >= 2:  # 至少有两个数字才认为是表格行
            # 提取行首的项目名称
            item_name = re.sub(r'[\d,，.%\-\s]+', '', line).strip()
            if item_name:
                rows.append({
                    "item": item_name,
                    "values": [n.replace(",", "").replace("，", "") for n in numbers]
                })
    
    return rows


def split_by_chinese_headers(text: str, source: str = "") -> list:
    """
    按中文财务报表标题分割文本
    
    支持的标题格式：
    - 一、二、三、... （中文数字序号）
    - 第一节、第二节、... （章节格式）
    - （一）（二）（三）... （括号格式）
    - 1、2、3、... 或 1.  2.  3. （阿拉伯数字序号）
    
    Args:
        text: 要分割的文本
        source: 来源文件路径
    
    Returns:
        分割后的 Document 列表
    """
    # 匹配中文财务报表常见的标题格式
    header_pattern = re.compile(
        r'^('
        r'[一二三四五六七八九十]+、|'                    # 一、二、三、
        r'第[一二三四五六七八九十\d]+[节章条款]|'        # 第一节、第二章
        r'[（(][一二三四五六七八九十\d]+[)）]|'          # （一）（二）(1)(2)
        r'\d+[、.．]\s*[^\d]|'                          # 1、 2. 3．
        r'[①②③④⑤⑥⑦⑧⑨⑩]'                           # 圈数字
        r')',
        re.MULTILINE
    )
    
    # 找到所有标题的位置
    matches = list(header_pattern.finditer(text))
    
    if not matches:
        # 没有找到标题，返回整个文本作为一个文档
        return [Document(page_content=text.strip(), metadata={"source": source, "header": "全文"})]
    
    documents = []
    
    for i, match in enumerate(matches):
        start = match.start()
        # 下一个标题的起始位置，或者文本末尾
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        
        chunk_text = text[start:end].strip()
        
        if chunk_text:
            # 提取标题作为元数据
            header_text = match.group(1).strip()
            # 获取标题后的第一行作为完整标题
            first_line = chunk_text.split('\n')[0][:50]  # 限制长度
            
            documents.append(Document(
                page_content=chunk_text,
                metadata={
                    "source": source,
                    "header": first_line,
                    "header_marker": header_text
                }
            ))
    
    # 如果第一个标题之前有内容，也作为一个文档
    if matches and matches[0].start() > 0:
        pre_content = text[:matches[0].start()].strip()
        if pre_content and len(pre_content) > 50:  # 忽略太短的前置内容
            documents.insert(0, Document(
                page_content=pre_content,
                metadata={"source": source, "header": "文档开头"}
            ))
    
    return documents


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
        "利润": ["利润总额", "归属于上市公司股东的净利润", "归属于上市公司股东的扣除非经常性损益的净利润"],
        "收入": ["营业收入", "营业总收入"],
        "资产": ["总资产", "资产总计"],
        "负债": ["总负债", "负债合计"],
        "现金流": ["经营活动产生的现金流量净额"],
        "毛利": ["毛利率"],
        "净利率": ["销售净利率"],
        "ROE": ["净资产收益率"],
        "ROA": ["总资产收益率"],
        "EPS": ["基本每股收益（元/股）", "稀释每股收益（元/股）"],
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
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        print(documents[0].page_content)
        print(f"✓ 已加载 {len(documents)} 页")
        
        # 保存原始内容
        pdf_content = "\n\n".join([doc.page_content for doc in documents])
        
        # 按标题分割（保持财务报表章节完整性）
        print("📝 正在按标题分割文本...")
        source = documents[0].metadata.get("source", pdf_path) if documents else pdf_path
        splits = split_by_chinese_headers(pdf_content, source)
        print(f"✓ 按标题分割，共 {len(splits)} 个章节")
        
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
  - 章节数: {len(splits)}（按标题分割）
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


def get_vectorstore():
    """获取当前的向量存储实例"""
    global pdf_vectorstore
    return pdf_vectorstore


def get_pdf_content():
    """获取当前的PDF原始内容"""
    global pdf_content
    return pdf_content


# 导出所有工具和函数
__all__ = [
    'load_financial_pdf',
    'search_financial_info',
    'extract_financial_data',
    'extract_financial_metrics',
    'extract_financial_table',
    'split_by_chinese_headers',
    'expand_query_with_synonyms',
    'extract_number_from_text',
    'get_vectorstore',
    'get_pdf_content',
    'pdf_vectorstore',
    'pdf_content',
]

