#!/usr/bin/env python3
"""
测试配置API的响应格式
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1"


def test_get_config():
    """测试获取配置API"""
    print("=== 测试获取配置API ===")
    try:
        response = requests.get(f"{BASE_URL}/config")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查响应格式
            if "data" in data:
                print("✓ 响应包含data字段")
                config_data = data["data"]
                
                # 检查各个配置节
                if "server" in config_data:
                    print(f"✓ 包含server配置: {config_data['server']}")
                if "llm" in config_data:
                    print(f"✓ 包含llm配置: {config_data['llm']}")
                if "embedding" in config_data:
                    print(f"✓ 包含embedding配置: {config_data['embedding']}")
            else:
                print("✗ 响应不包含data字段")
        else:
            print(f"✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print()


def test_update_config():
    """测试更新配置API"""
    print("=== 测试更新配置API ===")
    
    # 测试LLM配置更新
    llm_config = {
        "llm": {
            "service_type": "openai-compatible",
            "base_url": "http://localhost:11434/v1",
            "api_key": "",
            "model": "qwen2:7b",
            "max_tokens": 4096
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/config", json=llm_config)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查响应格式
            if "message" in data:
                print(f"✓ 响应包含message字段: {data['message']}")
            else:
                print("✗ 响应不包含message字段")
            
            if "needs_restart" in data:
                print(f"✓ 响应包含needs_restart字段: {data['needs_restart']}")
            else:
                print("✗ 响应不包含needs_restart字段")
            
            if "changed_keys" in data:
                print(f"✓ 响应包含changed_keys字段: {data['changed_keys']}")
            else:
                print("✗ 响应不包含changed_keys字段")
        else:
            print(f"✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print()
    
    # 测试Embedding配置更新
    embedding_config = {
        "embedding": {
            "service_type": "openai-compatible",
            "base_url": "http://localhost:8080/v1",
            "api_key": "",
            "model": "Qwen3-Embedding-4B",
            "dimensions": 1024
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/config", json=embedding_config)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查响应格式
            if "message" in data:
                print(f"✓ 响应包含message字段: {data['message']}")
            else:
                print("✗ 响应不包含message字段")
            
            if "needs_restart" in data:
                print(f"✓ 响应包含needs_restart字段: {data['needs_restart']}")
            else:
                print("✗ 响应不包含needs_restart字段")
            
            if "changed_keys" in data:
                print(f"✓ 响应包含changed_keys字段: {data['changed_keys']}")
            else:
                print("✗ 响应不包含changed_keys字段")
        else:
            print(f"✗ 请求失败: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print()


if __name__ == "__main__":
    test_get_config()
    test_update_config()
    print("=== 测试完成 ===")
