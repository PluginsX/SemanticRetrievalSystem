"""语义检索系统客户端使用示例

本文件展示了如何使用语义检索系统 Python 客户端库的各种功能。
"""

from semantic_retrieval_client import SemanticRetrievalClient
from semantic_retrieval_client.models import ArtifactCreate, ArtifactUpdate, SearchRequest
from semantic_retrieval_client.exceptions import APIError, ConnectionError, TimeoutError


def main():
    """客户端使用示例"""
    print("语义检索系统客户端使用示例")
    print("=" * 50)
    
    # 创建客户端实例
    try:
        client = SemanticRetrievalClient(
            base_url="http://localhost:8080/api/v1",
            # api_key="your-api-key-here"  # 如果需要 API 密钥，取消注释并填写
            timeout=300  # 5分钟超时
        )
        print("客户端初始化成功")
    except Exception as e:
        print(f"客户端初始化失败: {e}")
        return
    
    # 1. 健康检查
    print("\n1. 健康检查")
    print("-" * 30)
    try:
        health_status = client.health_check()
        print(f"状态: {health_status.status}")
        print(f"时间戳: {health_status.timestamp}")
        print("服务状态:")
        for service, status in health_status.services.items():
            print(f"  - {service}: {status}")
    except Exception as e:
        print(f"健康检查失败: {e}")
    
    # 2. 获取系统信息
    print("\n2. 获取系统信息")
    print("-" * 30)
    try:
        system_info = client.get_system_info()
        print(f"应用名称: {system_info.app_name}")
        print(f"版本: {system_info.version}")
        print(f"状态: {system_info.status}")
        print(f"环境: {system_info.environment}")
    except Exception as e:
        print(f"获取系统信息失败: {e}")
    
    # 3. 获取系统指标
    print("\n3. 获取系统指标")
    print("-" * 30)
    try:
        metrics = client.get_system_metrics()
        print(f"资料数量: {metrics.artifact_count}")
        print(f"切片数量: {metrics.chunk_count}")
        print(f"搜索次数: {metrics.search_count}")
        print(f"运行时间: {metrics.uptime} 秒")
    except Exception as e:
        print(f"获取系统指标失败: {e}")
    
    # 4. 获取资料列表
    print("\n4. 获取资料列表")
    print("-" * 30)
    try:
        artifacts_result = client.get_artifacts(page=1, size=10)
        print(f"总资料数: {artifacts_result['total_count']}")
        print(f"当前页码: {artifacts_result['page']}")
        print(f"每页数量: {artifacts_result['size']}")
        print("资料列表:")
        for artifact in artifacts_result['artifacts']:
            print(f"  - ID: {artifact['id']}, 标题: {artifact['title']}, 分类: {artifact.get('category', '未分类')}")
    except Exception as e:
        print(f"获取资料列表失败: {e}")
    
    # 5. 创建新资料
    print("\n5. 创建新资料")
    print("-" * 30)
    try:
        new_artifact = ArtifactCreate(
            title="测试资料",
            content="这是一个测试资料的内容，用于演示客户端库的创建资料功能。",
            category="测试",
            tags=["测试", "示例"]
        )
        created_artifact = client.create_artifact(new_artifact)
        print(f"创建成功！资料ID: {created_artifact.id}")
        print(f"标题: {created_artifact.title}")
        print(f"分类: {created_artifact.category}")
        print(f"标签: {created_artifact.tags}")
        
        # 保存创建的资料ID，用于后续操作
        test_artifact_id = created_artifact.id
    except Exception as e:
        print(f"创建资料失败: {e}")
        test_artifact_id = None
    
    # 6. 获取单个资料
    if test_artifact_id:
        print("\n6. 获取单个资料")
        print("-" * 30)
        try:
            artifact = client.get_artifact(test_artifact_id)
            print(f"资料ID: {artifact.id}")
            print(f"标题: {artifact.title}")
            print(f"内容: {artifact.content[:100]}...")  # 只显示前100个字符
            print(f"分类: {artifact.category}")
            print(f"标签: {artifact.tags}")
            print(f"创建时间: {artifact.created_at}")
        except Exception as e:
            print(f"获取资料失败: {e}")
    
    # 7. 更新资料
    if test_artifact_id:
        print("\n7. 更新资料")
        print("-" * 30)
        try:
            update_data = ArtifactUpdate(
                title="更新后的测试资料",
                content="这是更新后的资料内容，演示客户端库的更新资料功能。",
                category="测试更新"
            )
            updated_artifact = client.update_artifact(test_artifact_id, update_data)
            print(f"更新成功！")
            print(f"标题: {updated_artifact.title}")
            print(f"分类: {updated_artifact.category}")
        except Exception as e:
            print(f"更新资料失败: {e}")
    
    # 8. 执行向量检索
    print("\n8. 执行向量检索")
    print("-" * 30)
    try:
        search_result = client.search(
            query="测试资料",
            top_k=5,
            threshold=0.5
        )
        print(f"查询: {search_result.query}")
        print(f"找到 {search_result.total_count} 条相关资料")
        print(f"响应时间: {search_result.response_time:.2f} 秒")
        print("搜索结果:")
        for i, artifact in enumerate(search_result.artifacts, 1):
            similarity = artifact.get('similarity', 0)
            print(f"  {i}. {artifact['title']} (相似度: {similarity:.2f})")
    except Exception as e:
        print(f"搜索失败: {e}")
    
    # 9. 获取系统配置
    print("\n9. 获取系统配置")
    print("-" * 30)
    try:
        config = client.get_config()
        print("配置概览:")
        if 'server' in config:
            print(f"  服务器: {config['server']['host']}:{config['server']['port']}")
        if 'llm' in config:
            print(f"  LLM模型: {config['llm']['model']}")
        if 'embedding' in config:
            print(f"  Embedding模型: {config['embedding']['model']}")
            print(f"  向量维度: {config['embedding']['dimensions']}")
    except Exception as e:
        print(f"获取配置失败: {e}")
    
    # 10. 获取服务器日志
    print("\n10. 获取服务器日志")
    print("-" * 30)
    try:
        logs = client.get_server_logs(lines=10)
        print(f"最近 {len(logs)} 条服务器日志:")
        for log in logs[:5]:  # 只显示前5条
            print(f"  {log}")
        if len(logs) > 5:
            print("  ... (更多日志)")
    except Exception as e:
        print(f"获取日志失败: {e}")
    
    # 11. 删除测试资料
    if test_artifact_id:
        print("\n11. 删除测试资料")
        print("-" * 30)
        try:
            client.delete_artifact(test_artifact_id)
            print(f"删除成功！资料ID: {test_artifact_id}")
        except Exception as e:
            print(f"删除资料失败: {e}")
    
    print("\n" + "=" * 50)
    print("示例执行完成")


if __name__ == "__main__":
    main()
