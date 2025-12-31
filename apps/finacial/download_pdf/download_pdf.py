import requests
import time
import json
import os

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PDF 保存目录（相对于脚本位置的上级目录中的 pdf 文件夹）
PDF_DIR = os.path.join(SCRIPT_DIR, '..', 'pdf')

# 从 cookie.json 文件加载 cookies
def load_cookies_from_file(file_path):
    with open(file_path, "r", encoding='utf-8') as f:
        cookies_list = json.load(f)
    
    cookies_dict = {}
    for cookie in cookies_list:
        cookies_dict[cookie['name']] = cookie['value']
    
    return cookies_dict

# 1. 定义请求头
custom_headers = {
    # 模拟浏览器访问，很多网站会检查这个头
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    # 模拟认证，例如使用 Bearer Token
    'Authorization': 'Bearer your_secret_token_here',
    
    # 你可以添加其他任何需要的头，比如接受的语言等
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}
def download_pdf(url, filename):
    """
    从指定 URL 下载 PDF 文件并保存为本地文件。
    
    参数:
    url (str): PDF 文件的网络地址
    filename (str): 保存到本地的文件名（例如 'document.pdf'）
    """
    try:
        # 发送 GET 请求
        parsed_cookies = load_cookies_from_file("./cookie.json")
        response = requests.get(url, headers=custom_headers, cookies=parsed_cookies)
        # 以二进制写模式打开文件
        # 确保 pdf 目录存在
        os.makedirs(PDF_DIR, exist_ok=True)
        pdf_path = os.path.join(PDF_DIR, f"{filename}.pdf")
        with open(pdf_path, 'wb') as file:
            # 分块写入，避免大文件占用过多内存
            # for chunk in response.iter_content(chunk_size=8192):
            file.write(response.content)
        
        print(f"PDF 文件已成功下载并保存为: {filename}")
        
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
