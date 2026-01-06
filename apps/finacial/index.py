from typing import Any, Generator


from crawler_website.run_browser import run_browser
from download_pdf.auth_download import auth_download
from ai.analyse_pdf import analyse_pdf
from ai.index import main_with_pdf
from db.save_company_info import save_company_info
from db.search_SQL import search_SQL
from datetime import datetime
import logging
import asyncio
import os

# 配置日志
# 配置日志
logger = logging.getLogger(__name__)
if not logger.handlers:
    # 如果没有 handler，则添加一个
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

# 为了兼容现有代码中直接使用 logging.info 的情况
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True  # 强制重新配置 (Python 3.8+)
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(SCRIPT_DIR, 'pdf')



def main(exchange_code, stock_code, fiscal_year, company_name = '', period_type = 3) -> Generator:
    """
    主函数 - 返回生成器用于流式处理
    优化后的事件流：只保留关键节点，减少冗余事件
    """
    try:
        # 1. 初始化并查询数据库
        fiscal_year = datetime.now().year
        period_type = (datetime.now().month - 1) // 3 + 1
        logging.info(f"开始处理: exchange_code={exchange_code}, stock_code={stock_code}, fiscal_year={fiscal_year}, 季度={period_type}")
        
        yield {
            "status": "progress",
            "step": "query",
            "message": f"正在查询 {exchange_code}-{stock_code} 的财务数据..."
        }
        
        file = search_SQL(exchange_code, stock_code, fiscal_year, period_type)
        logging.info(f'数据库查询结果: {file}')
        
        # 2. 如果数据库没有数据，爬取网站
        if not file:
            logging.info("数据库中无数据，启动浏览器爬取...")
            yield {
                "status": "progress",
                "step": "crawl",
                "message": "数据库中无数据，正在爬取财务报表（可能需要10-30秒）..."
            }
            
            file = run_browser(exchange_code, stock_code, fiscal_year, period_type)
            save_company_info(file[0]['file_url'], exchange_code, stock_code, fiscal_year, period_type, file[0]['company_name'])
            logging.info(f"爬取并保存完成: {file[0]['company_name']}")
        else:
            logging.info(f"从数据库获取: {file[0]['company_name']}")
        
        # 3. 下载PDF文件
        company_name = file[0]['company_name']
        logging.info(f"开始下载PDF: {company_name}")
        yield {
            "status": "progress",
            "step": "download",
            "message": f"正在下载 {company_name} 的财务报表..."
        }
        
        auth_download(file[0]['file_url'], company_name)
        logging.info("PDF下载完成")

        # 4. AI分析PDF（流式输出）
        logging.info(f"开始AI分析: {company_name}")
        yield {
            "status": "progress",
            "step": "analyze_start",
            "message": f"开始AI分析 {company_name} 的财务报表..."
        }
        

        pdf_path = os.path.join(PDF_DIR, f"{company_name}.pdf")
        
        # 流式输出AI分析结果
        for analysis_chunk in main_with_pdf(pdf_path):
            yield {
                "status": "analyzing",
                "step": "analysis_stream",
                "data": analysis_chunk.get("content")
            }
            print(analysis_chunk, "analysis_chunk")
        
        # 5. 分析完成
        logging.info("财务报表分析完成")
        yield {
            "status": "complete",
            "message": "财务报表分析完成",
            "message": {
                "company_name": company_name,
                "exchange_code": exchange_code,
                "stock_code": stock_code,
                "fiscal_year": fiscal_year,
                "period_type": period_type
            }
        }
        
    except Exception as e:
        logging.error(f"执行出错: {str(e)}", exc_info=True)
        yield {
            "status": "error",
            "message": str(e)
        }


def main_async():
    for chunk in main('SZ', '000858', 2025):
       print(chunk.get('data', ''), end="", flush=True)

if __name__ == "__main__":
    logging.info("=" * 50)
    logging.info("开始执行财务报表分析系统")
    logging.info("=" * 50)
    try:
        main_async()
        logging.info("=" * 50)
        logging.info("执行完成")
        logging.info("=" * 50)
    except Exception as e:
        logging.error(f"执行出错: {str(e)}", exc_info=True)