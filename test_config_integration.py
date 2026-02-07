#!/usr/bin/env python3
"""
测试配置管理系统的完整集成流程
"""
import os
import sys
import yaml
from app.core.yaml_config import get_config_manager


def test_config_integration():
    """测试配置管理系统的完整集成流程"""
    print("=== 测试配置管理系统完整集成流程 ===")
    
    # 获取配置管理器实例
    config_manager = get_config_manager()
    print("✓ 获取配置管理器实例成功")
    
    # 测试场景1: 模拟前端更新服务器配置
    print("\n--- 测试场景1: 服务器配置 ---")
    server_config = {
        "server": {
            "host": "192.168.1.100",
            "port": 8888
        },
        "cors": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
        }
    }
    
    # 模拟后端处理
    current_config = config_manager.get_config()
    if "app" not in current_config:
        current_config["app"] = {}
    current_config["app"]["host"] = server_config["server"]["host"]
    current_config["app"]["port"] = server_config["server"]["port"]
    
    if "web_service" not in current_config:
        current_config["web_service"] = {}
    if "cors" not in current_config["web_service"]:
        current_config["web_service"]["cors"] = {}
    current_config["web_service"]["cors"]["allowed_origins"] = server_config["cors"]["origins"]
    
    config_manager.update_config(current_config)
    print("✓ 服务器配置更新成功")
    
    # 测试场景2: 模拟前端更新LLM配置
    print("\n--- 测试场景2: LLM配置 ---")
    llm_config = {
        "llm": {
            "service_type": "openai-compatible",
            "base_url": "http://localhost:11434/v1",
            "api_key": "test-api-key",
            "model": "qwen2:7b",
            "max_tokens": 4096
        }
    }
    
    # 模拟后端处理
    if "services" not in current_config:
        current_config["services"] = {}
    if "llm_services" not in current_config["services"]:
        current_config["services"]["llm_services"] = {}
    if "openai-compatible" not in current_config["services"]["llm_services"]:
        current_config["services"]["llm_services"]["openai-compatible"] = {}
    
    current_config["services"]["llm_services"]["openai-compatible"].update({
        "api_base": llm_config["llm"]["base_url"],
        "api_key": llm_config["llm"]["api_key"],
        "default_model": llm_config["llm"]["model"],
        "timeout": llm_config["llm"]["max_tokens"]
    })
    
    config_manager.update_config(current_config)
    print("✓ LLM配置更新成功")
    
    # 测试场景3: 模拟前端更新Embedding配置
    print("\n--- 测试场景3: Embedding配置 ---")
    embedding_config = {
        "embedding": {
            "service_type": "openai-compatible",
            "base_url": "http://localhost:11434/v1",
            "api_key": "test-api-key",
            "model": "qwen3-embedding-4b",
            "dimensions": 1024
        }
    }
    
    # 模拟后端处理
    if "services" not in current_config:
        current_config["services"] = {}
    if "embedding_services" not in current_config["services"]:
        current_config["services"]["embedding_services"] = {}
    if "openai-compatible" not in current_config["services"]["embedding_services"]:
        current_config["services"]["embedding_services"]["openai-compatible"] = {}
    
    current_config["services"]["embedding_services"]["openai-compatible"].update({
        "api_base": embedding_config["embedding"]["base_url"],
        "api_key": embedding_config["embedding"]["api_key"],
        "default_model": embedding_config["embedding"]["model"],
        "dimensions": embedding_config["embedding"]["dimensions"]
    })
    
    config_manager.update_config(current_config)
    print("✓ Embedding配置更新成功")
    
    # 验证最终配置
    print("\n--- 验证最终配置 ---")
    final_config = config_manager.get_config()
    
    # 验证服务器配置
    assert final_config["app"]["host"] == "192.168.1.100", "服务器host配置错误"
    assert final_config["app"]["port"] == 8888, "服务器port配置错误"
    assert final_config["web_service"]["cors"]["allowed_origins"] == ["http://localhost:3000", "http://127.0.0.1:3000"], "CORS配置错误"
    print("✓ 服务器配置验证通过")
    
    # 验证LLM配置
    llm_service_config = final_config["services"]["llm_services"]["openai-compatible"]
    assert llm_service_config["api_base"] == "http://localhost:11434/v1", "LLM base_url配置错误"
    assert llm_service_config["api_key"] == "test-api-key", "LLM api_key配置错误"
    assert llm_service_config["default_model"] == "qwen2:7b", "LLM model配置错误"
    assert llm_service_config["timeout"] == 4096, "LLM timeout配置错误"
    print("✓ LLM配置验证通过")
    
    # 验证Embedding配置
    embedding_service_config = final_config["services"]["embedding_services"]["openai-compatible"]
    assert embedding_service_config["api_base"] == "http://localhost:11434/v1", "Embedding base_url配置错误"
    assert embedding_service_config["api_key"] == "test-api-key", "Embedding api_key配置错误"
    assert embedding_service_config["default_model"] == "qwen3-embedding-4b", "Embedding model配置错误"
    assert embedding_service_config["dimensions"] == 1024, "Embedding dimensions配置错误"
    print("✓ Embedding配置验证通过")
    
    # 验证配置文件
    config_path = os.path.join(os.path.dirname(__file__), "config", "current_config.yaml")
    assert os.path.exists(config_path), "current_config.yaml文件不存在"
    print(f"✓ 配置文件已保存: {config_path}")
    
    print("\n=== 所有测试通过！配置管理系统集成正常 ===")


if __name__ == "__main__":
    test_config_integration()
