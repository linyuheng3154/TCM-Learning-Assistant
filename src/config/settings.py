"""
应用配置管理
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    app_name: str = "TCM Learning Assistant"
    version: str = "0.1.0"
    debug: bool = True
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI配置
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    
    # 数据配置
    data_dir: str = "data"
    
    class Config:
        env_file = ".env"

# 全局配置实例
_settings = None

def get_settings() -> Settings:
    """获取配置实例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings