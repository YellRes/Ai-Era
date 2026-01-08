"""
财务分析工具集
包含各种财务比率计算和分析相关的工具函数
"""

from langchain_core.tools import tool


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


# 导出所有工具
__all__ = [
    'calculate_financial_ratio',
    'analyze_profitability',
    'analyze_liquidity',
    'analyze_leverage',
]

