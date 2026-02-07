#!/usr/bin/env python3
"""
测试完整的配置管理功能
"""
import os
import sys
import yaml
from app.core.yaml_config import get_config_manager


def test_full_config():
    """测试完整的配置管理功能"""
    print("=== 测试完整的配置管理功能 ===")
    
    # 获取配置管理器实例
    config_manager = get_config_manager()
    print("✓ 获取配置管理器实例成功")
    
    # 获取当前配置
    current_config = config_manager.get_config()
    print(f"✓ 获取当前配置成功，配置项数量: {len(current_config)}")
    
    # 测试1: 测试服务器配置
    test_server_config = {
        "app": {
            "host": "192.168.1.100",
            "port": 8888
        },
        "web_service": {
            "cors": {
                "allowed_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
            }
        }
    }
    
    print("\n--- 测试1: 服务器配置 ---")
    config_manager.update_config(test_server_config)
    print("✓ 保存服务器配置成功")
    
    # 测试2: 测试LLM配置
    test_llm_config = {
        "services": {
            "llm_services": {
                "openai-compatible": {
                    "api_base": "http://localhost:11434/v1",
                    "api_key": "test-api-key",
                    "default_model": "qwen2:7b",
                    "timeout": 4096
                }
            }
        }
    }
    
    print("\n--- 测试2: LLM配置 ---")
    config_manager.update_config(test_llm_config)
    print("✓ 保存LLM配置成功")
    
    # 测试3: 测试Embedding配置
    test_embedding_config = {
        "services": {
            "embedding_services": {
                "openai-compatible": {
                    "api_base": "http://localhost:11434/v1",
                    "api_key": "test-api-key",
                    "default_model": "qwen3-embedding-4b",
                    "dimensions": 1024
                }
            }
        }
    }
    
    print("\n--- 测试3: Embedding配置 ---")
    config_manager.update_config(test_embedding_config)
    print("✓ 保存Embedding配置成功")
    
    # 测试4: 验证配置文件
    config_path = os.path.join(os.path.dirname(__file__), "config", "current_config.yaml")
    if os.path.exists(config_path):
        print(f"\n--- 测试4: 验证配置文件 ---")
        print(f"✓ current_config.yaml文件存在: {config_path}")
        
        # 读取文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✓ 读取配置文件成功，文件大小: {len(content)} bytes")
            
            # 解析YAML
            try:
                config_data = yaml.safe_load(content)
                print(f"✓ 解析配置文件成功，配置结构: {list(config_data.keys())}")
                
                # 验证服务器配置
                if "app" in config_data and "host" in config_data["app"] and config_data["app"]["host"] == "192.168.1.100":
                    print("✓ 服务器配置已正确保存")
                else:
                    print("✗ 服务器配置未正确保存")
                
                # 验证LLM配置
                if ("services" in config_data and "llm_services" in config_data["services"] and
                    "openai-compatible" in config_data["services"]["llm_services"]):
                    llm_config = config_data["services"]["llm_services"]["openai-compatible"]
                    if (llm_config.get("api_base") == "http://localhost:11434/v1" and
                        llm_config.get("default_model") == "qwen2:7b" and
                        llm_config.get("timeout") == 4096):
                        print("✓ LLM配置已正确保存")
                    else:
                        print("✗ LLM配置未正确保存")
                else:
                    print("✗ LLM配置未正确保存")
                
                # 验证Embedding配置
                if ("services" in config_data and "embedding_services" in config_data["services"] and
                    "openai-compatible" in config_data["services"]["embedding_services"]):
                    embedding_config = config_data["services"]["embedding_services"]["openai-compatible"]
                    if (embedding_config.get("api_base") == "http://localhost:11434/v1" and
                        embedding_config.get("api_key") == "test-api-key" and
                        embedding_config.get("default_model") == "qwen3-embedding-4b" and
                        embedding_config.get("dimensions") == 1024):
                        print("✓ Embedding配置已正确保存")
                    else:
                        print("✗ Embedding配置未正确保存")
                else:
                    print("✗ Embedding配置未正确保存")
                    
            except Exception as e:
                print(f"✗ 解析配置文件失败: {e}")
    else:
        print(f"✗ current_config.yaml文件不存在: {config_path}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_full_config()
