"""
财务分析工具集
统一导出所有财务分析相关的工具函数

本模块整合了两个子模块：
- pdf_loader: PDF 数据加载和提取工具
- pdf_analyzer: 财务分析和计算工具
"""

# 从 PDF 加载模块导入
from .pdf_loader import (
    load_financial_pdf,
    extract_financial_metrics,
    extract_financial_table,
    split_by_chinese_headers,
    extract_number_from_text,
    get_vectorstore,
    get_pdf_content,
    pdf_vectorstore,
    pdf_content,
)

# 从分析模块导入
from .pdf_analyzer import (
    calculate_financial_ratio,
    analyze_profitability,
    analyze_liquidity,
    analyze_leverage,
    analyze_qualitative_content,
)


# 导出所有工具
__all__ = [
    # PDF 加载工具
    'load_financial_pdf',
    'extract_financial_metrics',
    'extract_financial_table',
    'split_by_chinese_headers',
    'extract_number_from_text',
    'get_vectorstore',
    'get_pdf_content',
    'pdf_vectorstore',
    'pdf_content',
    # 分析工具
    'calculate_financial_ratio',
    'analyze_profitability',
    'analyze_liquidity',
    'analyze_leverage',
    'analyze_qualitative_content',
]
