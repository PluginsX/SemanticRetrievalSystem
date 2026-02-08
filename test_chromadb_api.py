"""测试ChromaDB API的embedding处理功能"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:12315"

def test_create_document_without_embedding():
    """测试创建文档时不提供embedding"""
    print("\n=== 测试1: 创建文档时不提供embedding ===")
    
    url = f"{BASE_URL}/api/v1/chromadb/documents"
    data = {
        "id": "test_doc_1",
        "document": "这是一个测试文档，用于验证自动生成embedding的功能",
        "metadata": {
            "test": "auto_embedding",
            "source": "test_script"
        }
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(url, json=data)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✓ 创建文档成功（自动生成embedding）")
        return True
    else:
        print("✗ 创建文档失败")
        return False

def test_create_document_with_embedding():
    """测试创建文档时提供embedding"""
    print("\n=== 测试2: 创建文档时提供embedding ===")
    
    url = f"{BASE_URL}/api/v1/chromadb/documents"
    
    # 生成一个假的embedding向量（1024维）
    embedding = [0.1] * 1024
    
    data = {
        "id": "test_doc_2",
        "document": "这是另一个测试文档，使用预计算的embedding",
        "metadata": {
            "test": "provided_embedding",
            "source": "test_script"
        },
        "embedding": embedding
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print(f"Embedding维度: {len(embedding)}")
    
    response = requests.post(url, json=data)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✓ 创建文档成功（使用提供的embedding）")
        return True
    else:
        print("✗ 创建文档失败")
        return False

def test_update_document_without_embedding():
    """测试更新文档时不提供embedding"""
    print("\n=== 测试3: 更新文档时不提供embedding ===")
    
    url = f"{BASE_URL}/api/v1/chromadb/documents/test_doc_1"
    data = {
        "document": "这是更新后的测试文档内容，应该保留原有的embedding",
        "metadata": {
            "test": "preserve_embedding",
            "source": "test_script",
            "updated": True
        }
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    response = requests.put(url, json=data)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✓ 更新文档成功（保留原有embedding）")
        return True
    else:
        print("✗ 更新文档失败")
        return False

def test_update_document_with_embedding():
    """测试更新文档时提供embedding"""
    print("\n=== 测试4: 更新文档时提供embedding ===")
    
    url = f"{BASE_URL}/api/v1/chromadb/documents/test_doc_2"
    
    # 生成一个新的embedding向量
    embedding = [0.2] * 1024
    
    data = {
        "document": "这是更新后的测试文档内容，使用新的embedding",
        "metadata": {
            "test": "new_embedding",
            "source": "test_script",
            "updated": True
        },
        "embedding": embedding
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print(f"新Embedding维度: {len(embedding)}")
    
    response = requests.put(url, json=data)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✓ 更新文档成功（使用新的embedding）")
        return True
    else:
        print("✗ 更新文档失败")
        return False

def test_get_documents():
    """获取文档列表"""
    print("\n=== 测试5: 获取文档列表 ===")
    
    url = f"{BASE_URL}/api/v1/chromadb/documents"
    
    response = requests.get(url)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"文档总数: {result['data']['total']}")
        print(f"返回文档数: {len(result['data']['records'])}")
        
        for doc in result['data']['records']:
            print(f"\n文档ID: {doc['id']}")
            print(f"文档内容: {doc['document'][:50]}...")
            print(f"元数据: {doc['metadata']}")
        
        return True
    else:
        print("✗ 获取文档列表失败")
        return False

def test_search_documents():
    """搜索文档"""
    print("\n=== 测试6: 搜索文档 ===")
    
    url = f"{BASE_URL}/api/v1/chromadb/documents/search"
    data = {
        "query": "测试文档",
        "top_k": 5,
        "threshold": 0.0
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(url, json=data)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"搜索结果数: {result['data']['total']}")
        
        for doc in result['data']['records']:
            print(f"\n文档ID: {doc['id']}")
            print(f"相似度: {doc['similarity']:.4f}")
            print(f"距离: {doc['distance']:.4f}")
            print(f"文档内容: {doc['document'][:50]}...")
        
        return True
    else:
        print("✗ 搜索文档失败")
        return False

def cleanup():
    """清理测试文档"""
    print("\n=== 清理测试文档 ===")
    
    test_ids = ["test_doc_1", "test_doc_2"]
    
    for doc_id in test_ids:
        url = f"{BASE_URL}/api/v1/chromadb/documents/{doc_id}"
        response = requests.delete(url)
        if response.status_code == 200:
            print(f"✓ 删除文档 {doc_id} 成功")
        else:
            print(f"✗ 删除文档 {doc_id} 失败")

def main():
    print("=" * 60)
    print("ChromaDB API Embedding处理功能测试")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("创建文档（自动生成embedding）", test_create_document_without_embedding()))
        time.sleep(1)
        
        results.append(("创建文档（提供embedding）", test_create_document_with_embedding()))
        time.sleep(1)
        
        results.append(("更新文档（保留embedding）", test_update_document_without_embedding()))
        time.sleep(1)
        
        results.append(("更新文档（使用新embedding）", test_update_document_with_embedding()))
        time.sleep(1)
        
        results.append(("获取文档列表", test_get_documents()))
        time.sleep(1)
        
        results.append(("搜索文档", test_search_documents()))
        
    finally:
        time.sleep(1)
        cleanup()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")

if __name__ == "__main__":
    main()