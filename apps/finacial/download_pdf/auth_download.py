from playwright.sync_api import sync_playwright
from .download_pdf import download_pdf
import json
def auth_download(url, filename):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 可设为 True
        context = browser.new_context()
        page = context.new_page()

        def handle_response(response):
            # 检查响应是否为 PDF 文件
            if response.headers.get("content-type") == "application/pdf":
                with open(f"./cookie.json", "w", encoding='utf-8') as f:
                    print(context.cookies(), 'context.cookies()')
                    json.dump(context.cookies(), f, ensure_ascii=False, indent=4)
                download_pdf(url, filename)

        # 注册响应监听器
        page.on("response", handle_response)
        # page.wait_for_load_state("networkidle")
        # 场景1：直接访问 PDF 链接
        page.goto(url)  # 替换为你的 PDF URL
        # 浏览器保持打开状态，等待下载完成
        page.wait_for_timeout(10000)  # 等待一段时间以确保下载完成


