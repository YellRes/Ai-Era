import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载 .env 文件中的环境变量
_ = load_dotenv()

# 1. 配置认证信息 (建议放入环境变量)
url: str | None = os.environ.get("SUPABASE_URL")
key: str | None = os.environ.get("SUPABASE_KEY") # 使用 service_role key 可以绕过 RLS 权限

# 2. 初始化客户端
if not url or not key:
    raise ValueError("SUPABASE_URL 和 SUPABASE_KEY 环境变量未设置")
supabase: Client = create_client(url, key)

