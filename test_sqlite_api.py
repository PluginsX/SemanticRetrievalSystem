#!/usr/bin/env python3
"""
测试SQLite API的调用
"""
import requests
import json

BASE_URL = "http://localhost:12315/api/v1"

def test_sqlite_api():
    """测试SQLite数据库管理API"""
    print("=== 测试SQLite API ===")
    
    # 测试获取表数据
    print("\n1. 测试获取SQLite表数据:")
    try:
        response = requests.get(f"{BASE_URL}/sqlite/tables/artifacts", params={"page": 1, "size": 20})
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应内容: {response.text}")
        print(f"响应JSON: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_sqlite_api()
