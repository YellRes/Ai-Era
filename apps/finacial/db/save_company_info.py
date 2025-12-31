from datetime import datetime
from .index import supabase
import logging

def save_company_info(url: str, exchange_code: str, stock_code: str, fiscal_year: int, period_type: int, company_name: str):
    """
    保存公司财务报表信息到数据库
    
    Args:
        url: 报表文件URL
        exchange_code: 交易所代码 (如 'SH')
        stock_code: 股票代码
        fiscal_year: 财政年份
        period_type: 报表期间类型 (1-4 表示四个季度)
    """
    try:
        data = {
            "file_url": url,
            "exchange_code": exchange_code,
            "stock_code": stock_code,
            "fiscal_year": fiscal_year,
            "period_type": period_type,
            "company_name": company_name
        }
        
        response = supabase.table("financial_reports").insert(data).execute()
        logging.info(f"公司信息保存成功: {response.data}")
        return response.data
    except Exception as e:
        logging.error(f"保存公司信息失败: {str(e)}", exc_info=True)
        raise