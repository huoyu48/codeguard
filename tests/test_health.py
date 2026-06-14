"""健康检查测试"""
from app.config import Settings


def test_settings_defaults():
    """测试配置默认值"""
    settings = Settings()
    assert settings.deepseek_model == "deepseek-chat"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"


def test_health_endpoint():
    """测试健康检查端点（不需要启动服务器）"""
    from app.main import app
    assert app.title == "CodeGuard API"
