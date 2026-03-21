"""
统一的 Zep 客户端工厂
"""

from typing import Optional
from zep_python import Zep
from ..config import Config

def get_zep_client(api_key: Optional[str] = None) -> Zep:
    """
    获取标准化配置的 Zep 客户端。
    强制优先使用本地 Docker 部署 (http://localhost:8000)。
    """
    # 始终优先使用本地 URL，如果未在环境变量中设置，则使用默认的 Docker 端口
    base_url = Config.ZEP_API_URL or "http://localhost:8000"
    
    # 本地 Zep 通常不需要 API key，但为了兼容 SDK，我们传递一个默认字符串或环境变量中的 key
    key = api_key or Config.ZEP_API_KEY or "local_dev_key"
    
    return Zep(api_key=key, base_url=base_url)
