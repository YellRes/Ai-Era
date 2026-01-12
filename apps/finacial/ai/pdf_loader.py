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


def format_amount(value: float) -> str:
    """
    格式化金额,自动转换为万/亿单位
    
    Args:
        value: 金额数值
    
    Returns:
        格式化后的字符串
    """
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 100_000_000:  # 大于等于1亿
        return f"{sign}{abs_value / 100_000_000:.2f} 亿元"
    elif abs_value >= 10_000:  # 大于等于1万
        return f"{sign}{abs_value / 10_000:.2f} 万元"
    else:
        return f"{sign}{abs_value:.2f} 元"

@tool
def extract_financial_metrics(query: str = "all") -> str:
    """
    从已加载的财务报表 PDF 中提取关键财务指标（营业收入、净利润、资产状况等）。
    
    Args:
        query: 提取模式，默认为 "all"。
    
    Returns:
        包含财务指标的格式化报告。
    """
    global pdf_content
    
    if pdf_content is None:
        return "❌ 请先使用 load_financial_pdf 工具加载 PDF 文件"
    
    # 定义要提取的财务指标及其正则模式
    patterns = {
        # 利润表指标 (每个汉字之间都允许空白符)
        "营业收入": r"营[\s\n]*业[\s\n]*(?:总[\s\n]*)?收[\s\n]*入[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*([\d,，]+\.?\d*)",
        "利润总额": r"利[\s\n]*润[\s\n]*总[\s\n]*额[（(]?元?[)）]?[\s\n|｜]*(?:—[\s\n]*)*([\d,，]+\.?\d*)",
        "归属于上市公司股东的净利润": r"归[\s\n]*属[\s\n]*于[\s\n]*上[\s\n]*市[\s\n]*公[\s\n]*司[\s\n]*股[\s\n]*东[\s\n]*的?[\s\n]*净[\s\n]*利[\s\n]*润[\s\n]*[（(]?[\s\n]*元?[\s\n]*[)）]?[\s\n|｜]*(?:—[\s\n]*)*(-?[\d,，]+\.?\d*)",
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
    
    # 定义哪些指标是金额类型(需要格式化)
    amount_metrics = {
        "营业收入", "利润总额", "归属于上市公司股东的净利润", 
        "扣非净利润", "总资产", "归属于上市公司股东的所有者权益",
        "经营活动产生的现金流量净额"
    }
    
    result = "📊 提取的财务指标：\n\n"
    found_any = False
    
    for name, pattern in patterns.items():
        match = re.search(pattern, pdf_content)
        if match:
            found_any = True
            value_str = match.group(1).replace(",", "").replace("，", "")
            try:
                value = float(value_str)
                if name in amount_metrics:
                    result += f"- {name}: {format_amount(value)}\n"
                else:
                    result += f"- {name}: {value}\n"
            except:
                result += f"- {name}: {value_str}\n"
                
    if not found_any:
        return "❓ 未能在 PDF 中提取到关键财务指标，可能需要手动搜索。"
        
    return result


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
    'extract_financial_metrics',
    'extract_financial_table',
    'split_by_chinese_headers',
    'extract_number_from_text',
    'get_vectorstore',
    'get_pdf_content',
    'pdf_vectorstore',
    'pdf_content',
]

