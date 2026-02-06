"""语义检索系统客户端库安装配置"""

from setuptools import setup, find_packages

setup(
    name="semantic-retrieval-client",
    version="1.0.0",
    description="语义检索系统 Python 客户端库",
    long_description="""语义检索系统 Python 客户端库

本客户端库提供了与语义检索系统 API 交互的便捷方法，支持资料管理、智能检索、系统配置等功能。

主要功能：
- 资料管理：获取、创建、更新、删除资料
- 智能检索：执行向量检索，获取相关资料
- 系统服务：健康检查、系统信息、系统指标
- 配置管理：获取、更新系统配置，测试 LLM 和 Embedding 配置
- 日志管理：获取服务器和数据库日志

使用示例：
```python
from semantic_retrieval_client import SemanticRetrievalClient

# 创建客户端实例
client = SemanticRetrievalClient(
    base_url="http://localhost:8080/api/v1",
    api_key="your-api-key-here"
)

# 获取资料列表
artifacts = client.get_artifacts(page=1, size=10)

# 执行向量检索
search_results = client.search("青铜器的历史", top_k=5)
```
""",
    long_description_content_type="text/markdown",
    url="https://github.com/PluginsX/SemanticRetrievalSystem",
    project_urls={
        "Documentation": "https://semantic-retrieval-system.readthedocs.io/",
        "Source": "https://github.com/PluginsX/SemanticRetrievalSystem/",
        "Tracker": "https://github.com/PluginsX/SemanticRetrievalSystem/issues/"
    },
    author="Semantic Retrieval System Team",
    author_email="contact@semantic-retrieval-system.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Client"
    ],
    python_requires=">=3.9",
    keywords="semantic retrieval client api",
)
