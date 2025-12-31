"""
深圳证券交易所定期报告爬虫模块
使用 Playwright 自动化浏览器获取上市公司定期报告下载链接
"""

from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

# 深交所基础 URL
BASE_URL = "https://www.szse.cn"


def shengzhen_browser(page, searchWord):
    """
    在深交所网站搜索定期报告并返回第一条结果的下载链接
    
    Args:
        page: Playwright 的 Page 对象（sync_api）
        searchWord: 搜索关键字（股票代码/简称/拼音/标题关键字）
    
    Returns:
        str: 第一条结果的下载链接 URL，如果没有结果则返回空字符串
    """
    # 1. 导航到深交所首页
    page.goto("https://www.szse.cn/disclosure/listed/fixed/index.html")
    page.wait_for_load_state("networkidle")
    
    # 4. 等待页面加载完成
    page.wait_for_load_state("networkidle")
    
    # 5. 在搜索框中输入搜索关键字
    search_input = page.locator("#input_code")
    search_input.fill(searchWord)
    
    # 6. 点击查询按钮并等待网络请求完成
    query_button = page.locator("#query-btn")

    page.locator(".c-loading-overlay").wait_for(state="detached", timeout=6000)

    query_button.click()
    
    # 使用 expect_response 等待 AJAX 请求完成
    # with page.expect_response(
    #     lambda response: "disclosure" in response.url and response.status == 200,
    #     timeout=30000
    # ) as response_info:
        
    print("点击查询按钮成功")
    # 等待表格数据加载
    # page.wait_for_timeout(5000)
    page.locator(".c-loading-overlay").wait_for(state="detached", timeout=6000)

    # 方法1：通过父容器 class 和链接定位
    company_link = page.locator(".disclosure-tbody .title-name a").first
    company_name = company_link.get_attribute("title")  # "平安银行"
    print(f"获取到的公司名称: {company_name}")
    
    # 7. 获取第一行的下载链接
    title_span = page.locator(".disclosure-tbody .annon-title-link").first.get_attribute("href")
    print(f"获取到的链接: {title_span}")
    page.goto("https://www.szse.cn" + title_span)
    
    # 等待页面加载完成
    page.wait_for_load_state("networkidle")

    pdf_url = page.locator("#annouceDownloadBtn").get_attribute("href")

    res = []
    res.append({
        'company_name': company_name,
        'file_url': pdf_url.replace('/download', '')
    })
    print(f"获取到的链接: {res}")
    return res
    
    # 获取下载链接
    # download_link = page.locator(".disclosure-tbody a").first
    # return download_link.get_attribute("href")



def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, timeout=400000)  # headless=False 表示可以看到浏览器界面
        page = browser.new_page()
        result = shengzhen_browser(page, '000001')
        print(f"获取到的链接: {result}")
        browser.close()

if __name__ == "__main__":
    main()
