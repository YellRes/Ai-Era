from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import json
import requests
from index import main
from fastapi.middleware.cors import CORSMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="财务报表分析系统")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 地址
    allow_methods=["*"],
    allow_headers=["*"],
)
class FinancialRequest(BaseModel):
    exchange_code: str  # 交易所代码 (如 'SH')
    stock_code: str     # 股票代码
    fiscal_year: int    # 财政年份
    company_name: str = ""
    period_type: int = 3

@app.get("/")
def read_root():
    return {"message": "财务报表分析系统 API"}

@app.get("/get_company_info")
def get_company_info():
    url = "http://www.cninfo.com.cn/new/data/szse_stock.json"
    response = requests.get(url)
    data = response.json()
    return data

@app.post("/analyze")
def analyze_financial_report(request: FinancialRequest):
    """
    分析财务报表 - 流式响应
    """
    def event_generator():
        try:
            logging.info(f"收到请求: {request}")
            
            # 从 main 函数获取生成器
            for event in main(
                request.exchange_code,
                request.stock_code,
                request.fiscal_year,
                request.company_name,
                request.period_type
            ):
                # 转换为 JSON 并使用 SSE 格式发送
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            logging.error(f"处理失败: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
    
    print(request, "analyze")
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)