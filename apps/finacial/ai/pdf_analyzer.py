"""
财务分析工具集
包含各种财务比率计算和分析相关的工具函数
"""

from langchain_core.tools import tool
from typing import Literal


@tool
def calculate_financial_ratio(
    metric: Literal['ROE', 'ROA', 'current_ratio', 'debt_ratio', 'profit_margin'], 
    numerator: float, 
    denominator: float
) -> str:
    """
    计算并在必要时格式化特定的财务比率。

    Args:
        metric: 要计算的具体财务指标。必须是以下之一：
            - 'ROE': 净资产收益率 (Net Income / Equity)
            - 'ROA': 总资产收益率 (Net Income / Total Assets)
            - 'current_ratio': 流动比率 (Current Assets / Current Liabilities)
            - 'debt_ratio': 资产负债率 (Total Liabilities / Total Assets)
            - 'profit_margin': 利润率 (Net Income / Revenue)
        numerator: 分子数值 (例如净利润、流动资产等)
        denominator: 分母数值 (例如归属于母公司股东权益、流动负债等)
    
    Returns:
        str: 格式化后的比率字符串（百分比或小数形式）。
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
def analyze_profitability(
    revenue: float = 0, 
    net_income: float = 0, 
    total_assets: float = 0, 
    operating_income: float = 0,
    auto_extract: bool = True
) -> str:
    """
    生成一份关于企业盈利能力的综合分析报告。
    
    该工具会计算利润率、ROA、扣非净利率，并根据内置的财务健康标准生成文字评价。
    
    Args:
        revenue: 营业收入 (Total Revenue)，默认0时自动提取
        net_income: 净利润 (Net Income)，默认0时自动提取
        total_assets: 总资产 (Total Assets)，默认0时自动提取
        operating_income: 扣除非经常性损益后的净利润，默认0时自动提取
        auto_extract: 是否自动从 PDF 提取数据（默认 True）
    
    Returns:
        str: 包含各项指标计算结果和定性分析结论的文本报告。
    """
    # 自动提取数据
    if auto_extract and (revenue == 0 or net_income == 0 or total_assets == 0):
        from .pdf_loader import get_extracted_metrics
        metrics = get_extracted_metrics()
        
        if not metrics:
            return "❌ 无法自动提取数据，请先使用 load_financial_pdf 加载 PDF 文件，或手动传入参数。"
        
        if revenue == 0:
            revenue = metrics.get("营业收入", 0)
        if net_income == 0:
            net_income = metrics.get("归属于上市公司股东的净利润", 0)
        if total_assets == 0:
            total_assets = metrics.get("总资产", 0)
        if operating_income == 0:
            operating_income = metrics.get("扣非净利润", 0)
    
    if revenue == 0 or total_assets == 0:
        return "错误：收入或总资产不能为零（无法从 PDF 中提取或未传入有效值）"
    
    profit_margin = (net_income / revenue) * 100
    roa = (net_income / total_assets) * 100
    operating_profit_margin = (operating_income / revenue) * 100 if operating_income != 0 else 0
    
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
    
    analysis += f"- 归属于上市公司股东的扣除非经常性损益的净利润率: {operating_profit_margin:.2f}%"
    return analysis


@tool
def analyze_liquidity(
    current_assets: float = 0, 
    current_liabilities: float = 0, 
    cash: float = 0, 
    inventory: float = 0,
    auto_extract: bool = True
) -> str:
    """
    生成一份关于企业短期偿债能力（流动性）的综合分析报告。
    
    该工具会计算流动比率、速动比率和现金比率，并评估短期债务风险。
    
    Args:
        current_assets: 流动资产合计，默认0时自动提取
        current_liabilities: 流动负债合计，默认0时自动提取
        cash: 货币资金/现金及现金等价物，默认0时自动提取
        inventory: 存货，默认0时自动提取
        auto_extract: 是否自动从 PDF 提取数据（默认 True）
    
    Returns:
        str: 包含流动性指标和风险评估的文本报告。
    """
    # 自动提取数据
    if auto_extract and (current_assets == 0 or current_liabilities == 0):
        from .pdf_loader import get_extracted_metrics
        metrics = get_extracted_metrics()
        
        if not metrics:
            return "❌ 无法自动提取数据，请先使用 load_financial_pdf 加载 PDF 文件，或手动传入参数。"
        
        if current_assets == 0:
            current_assets = metrics.get("流动资产合计", 0)
        if current_liabilities == 0:
            current_liabilities = metrics.get("流动负债合计", 0)
        if cash == 0:
            cash = metrics.get("货币资金", 0)
        if inventory == 0:
            inventory = metrics.get("存货", 0)
    
    # 检查是否有足够数据进行分析
    missing_fields = []
    if current_assets == 0:
        missing_fields.append("流动资产合计")
    if current_liabilities == 0:
        missing_fields.append("流动负债合计")
    
    if missing_fields:
        return f"⚠️ 无法进行流动性分析，缺少以下数据：{', '.join(missing_fields)}\n\n请检查 PDF 中是否包含资产负债表详细信息，或手动传入参数。"
    
    current_ratio = current_assets / current_liabilities
    quick_ratio = (current_assets - inventory) / current_liabilities if inventory > 0 else current_ratio
    cash_ratio = cash / current_liabilities if cash > 0 else 0
    
    analysis = f"""
💰 流动性分析报告：
- 流动比率: {current_ratio:.2f}
- 速动比率: {quick_ratio:.2f}
"""
    
    if cash > 0:
        analysis += f"- 现金比率: {cash_ratio:.2f}\n"
    else:
        analysis += "- 现金比率: 数据不足\n"
    
    analysis += "\n💡 分析结论：\n"
    
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
def analyze_leverage(
    total_assets: float = 0, 
    total_liabilities: float = 0, 
    equity: float = 0, 
    interest_expense: float = 0, 
    ebit: float = 0,
    auto_extract: bool = True
) -> str:
    """
    生成一份关于企业长期偿债能力（杠杆）的综合分析报告。
    
    该工具会分析资本结构（资产负债率、权益乘数）和利息覆盖能力。
    
    Args:
        total_assets: 资产总计，默认0时自动提取
        total_liabilities: 负债合计，默认0时自动提取
        equity: 所有者权益（或股东权益）合计，默认0时自动提取
        interest_expense: 利息费用（财务费用中的利息支出）- 如果未知请传 0
        ebit: 息税前利润 (通常用 净利润 + 利息费用 + 所得税 估算) - 如果未知请传 0
        auto_extract: 是否自动从 PDF 提取数据（默认 True）
    
    Returns:
        str: 包含资本结构分析和偿债压力评估的文本报告。
    """
    # 自动提取数据
    if auto_extract and (total_assets == 0 or total_liabilities == 0 or equity == 0):
        from .pdf_loader import get_extracted_metrics
        metrics = get_extracted_metrics()
        
        if not metrics:
            return "❌ 无法自动提取数据，请先使用 load_financial_pdf 加载 PDF 文件，或手动传入参数。"
        
        if total_assets == 0:
            total_assets = metrics.get("总资产", 0)
        if total_liabilities == 0:
            total_liabilities = metrics.get("负债合计", 0)
        if equity == 0:
            equity = metrics.get("归属于上市公司股东的所有者权益", 0)
    
    # 检查是否有足够数据进行分析
    missing_fields = []
    if total_assets == 0:
        missing_fields.append("总资产")
    if equity == 0:
        missing_fields.append("股东权益")
    
    if missing_fields:
        return f"⚠️ 无法进行杠杆分析，缺少以下数据：{', '.join(missing_fields)}\n\n请检查 PDF 中是否包含相关信息，或手动传入参数。"
    
    # 如果没有负债数据，尝试通过 总资产 - 股东权益 计算
    if total_liabilities == 0 and total_assets > 0 and equity > 0:
        total_liabilities = total_assets - equity
    
    debt_ratio = (total_liabilities / total_assets) * 100 if total_liabilities > 0 else 0
    equity_ratio = (equity / total_assets) * 100
    debt_to_equity = total_liabilities / equity if equity != 0 and total_liabilities > 0 else 0
    
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
def analyze_qualitative_content(
    topic: Literal['business_review', 'future_outlook', 'risk_factors', 'management_discussion']
) -> str:
    """
    分析 PDF 中的非数值性（定性）内容，如经营情况、未来展望或风险因素。
    
    该工具会执行语义搜索并返回相关的文本片段，供 LLM 进行综合分析。
    
    Args:
        topic: 要分析的主题：
            - 'business_review': 业务回顾与主要业务概况
            - 'future_outlook': 公司未来发展的展望与计划
            - 'risk_factors': 公司面临的风险因素与不确定性
            - 'management_discussion': 管理层对经营情况的讨论与分析 (MD&A)
            
    Returns:
        str: 检索到的相关文本片段。
    """
    from .pdf_loader import get_vectorstore, get_pdf_content
    
    vs = get_vectorstore()
    if vs is None:
        return "错误：PDF 尚未加载，请先使用 load_financial_pdf。"
    
    pdf_content = get_pdf_content()
        
    # 定义主题关键词以增强检索效果
    topic_keywords = {
        'business_review': '主要业务情况 经营情况回顾 业务概要 主营业务',
        'future_outlook': '未来展望 发展战略 经营计划 行业发展趋势 发展规划',
        'risk_factors': '风险因素 可能面对的风险 应对措施 风险提示 不确定性',
        'management_discussion': '管理层讨论与分析 经营情况讨论 董事会报告 经营分析'
    }
    
    topic_names = {
        'business_review': '业务回顾',
        'future_outlook': '未来展望',
        'risk_factors': '风险因素',
        'management_discussion': '管理层讨论'
    }
    
    query = topic_keywords.get(topic, topic)
    topic_name = topic_names.get(topic, topic)
    
    # 增加检索数量以获取更多候选
    docs = vs.similarity_search(query, k=8)
    
    if not docs:
        return f"未找到关于 '{topic_name}' 的相关内容。"
    
    # 过滤太短的片段（少于100字符的可能只是标题）
    MIN_CONTENT_LENGTH = 100
    valid_docs = []
    
    for doc in docs:
        content = doc.page_content.strip()
        if len(content) >= MIN_CONTENT_LENGTH:
            valid_docs.append(doc)
        elif pdf_content and len(content) > 20:
            # 尝试从原始内容中扩展上下文
            # 找到这段文字在原始内容中的位置
            pos = pdf_content.find(content[:50])  # 用前50字符定位
            if pos != -1:
                # 扩展上下文：前后各取500字符
                start = max(0, pos - 200)
                end = min(len(pdf_content), pos + len(content) + 500)
                expanded_content = pdf_content[start:end].strip()
                if len(expanded_content) >= MIN_CONTENT_LENGTH:
                    # 创建扩展后的文档
                    from langchain_core.documents import Document
                    expanded_doc = Document(
                        page_content=expanded_content,
                        metadata={**doc.metadata, "expanded": True}
                    )
                    valid_docs.append(expanded_doc)
    
    # 取前5个有效片段
    valid_docs = valid_docs[:5]
    
    if not valid_docs:
        return f"未找到关于 '{topic_name}' 的有效内容片段（检索到的内容过短）。"
        
    result = f"🔍 关于 '{topic_name}' 的检索结果：\n\n"
    for i, doc in enumerate(valid_docs, 1):
        header = doc.metadata.get("header", "未知章节")
        expanded_mark = " (已扩展上下文)" if doc.metadata.get("expanded") else ""
        result += f"--- 片段 {i}{expanded_mark} [来源: {header}] ---\n"
        result += f"{doc.page_content}\n\n"
        
    return result


# 导出所有工具
__all__ = [
    'calculate_financial_ratio',
    'analyze_profitability',
    'analyze_liquidity',
    'analyze_leverage',
    'analyze_qualitative_content',
]

