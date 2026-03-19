"""
应用配置管理
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置"""
    
    model_config = SettingsConfigDict(env_file=".env")
    
    # 应用配置
    app_name: str = "TCM Learning Assistant"
    version: str = "0.4.1"
    debug: bool = True
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # AI服务配置
    ai_api_key: str = ""
    ai_base_url: str = ""
    
    # 数据配置
    data_dir: str = "data"

# 全局配置实例
_settings = None

def get_settings() -> Settings:
    """获取配置实例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings