from langchain_community.document_loaders import PyMuPDFLoader
from tools import extract_financial_metrics, extract_financial_table

def read_pdf(pdf_path: str):
    """读取 PDF 文件"""
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    return documents


if __name__ == "__main__":
    pdf_path = "../pdf/600143金发科技2025年第三季度报告.pdf"
    
    # 1. 加载 PDF
    documents = read_pdf(pdf_path)
    print(f"📄 共加载 {len(documents)} 页\n")
    
    # 2. 提取财务指标
    print("=" * 50)
    print("📊 提取的财务指标：")
    print("=" * 50)
    metrics = extract_financial_metrics(documents)
    for name, value in metrics.items():
        if isinstance(value, float):
            if value > 1000000:
                print(f"  {name}: {value:,.2f} 元")
            else:
                print(f"  {name}: {value}")
        else:
            print(f"  {name}: {value}")
    
    # 3. 提取第 2 页（主要财务数据页）的表格数据
    print("\n" + "=" * 50)
    print("📋 第 2 页表格数据：")
    print("=" * 50)
    if len(documents) > 1:
        table_rows = extract_financial_table(documents[1].page_content)
        for row in table_rows[:10]:  # 只显示前 10 行
            print(f"  {row['item']}: {row['values']}")