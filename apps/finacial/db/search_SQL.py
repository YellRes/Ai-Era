from .index import supabase
def search_SQL(exchange_code, stock_code, fiscal_year, period_type):
    query = supabase.table('financial_reports').select('*').eq('exchange_code', exchange_code).eq('stock_code', stock_code).eq('fiscal_year', fiscal_year).eq('period_type', period_type)
    response = query.execute()
    # 判断 response.data 是否为数组，为数组则返回第一个元素，否则返回 None
    if isinstance(response.data, list) and len(response.data) > 0:
        return response.data
    return None

# if __name__ == "__main__":
    # search_SQL('SH', '600000', 2023, 1)