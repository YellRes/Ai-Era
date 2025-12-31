from playwright.sync_api import sync_playwright
from .shanghai import shanghai_browser
from .beijing import beijing_browser
from .shengzhen import shengzhen_browser

def run_browser(exchange_code, stock_code, fiscal_year, period_type):
    res = []
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False, timeout=400000)  # headless=False 表示可以看到浏览器界面
        
        # 创建新页面
        page = browser.new_page()
        
        # 设置全局超时时间（毫秒）
        page.set_default_timeout(60000)  # 所有操作默认 60 秒
        page.set_default_navigation_timeout(60000)  # 导航操作默认 60 秒
        
        match exchange_code:
            case 'SH':
                res = shanghai_browser(page, stock_code)
            case 'SZ':
                res = shengzhen_browser(page, stock_code)
            case 'BJ':
                res = beijing_browser(page, stock_code)
            case _:
                raise ValueError(f"不支持的交易所: {exchange_code}")
   
    return res

if __name__ == "__main__":
    run_browser('')