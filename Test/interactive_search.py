"""交互式检索测试脚本

使用语义检索系统客户端库构建的交互式检索程序，
在控制台中接收用户输入的检索字符串，发送到服务器并显示结果。
"""

import sys
import os

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 导入客户端库模块
from Client.client import SemanticRetrievalClient
from Client.exceptions import APIError, ConnectionError, TimeoutError


def print_header():
    """打印程序头部信息"""
    print("=" * 80)
    print("语义检索系统 - 交互式检索测试")
    print("=" * 80)
    print("输入检索字符串并按回车发送请求，输入 'exit' 退出程序")
    print("=" * 80)


def print_footer():
    """打印程序底部信息"""
    print("=" * 80)
    print("程序已退出")
    print("=" * 80)


def print_search_result(result):
    """打印搜索结果
    
    Args:
        result: 搜索结果对象
    """
    print("\n" + "-" * 60)
    print(f"检索查询: {result.query}")
    print(f"找到 {result.total_count} 条相关资料")
    print(f"响应时间: {result.response_time:.2f} 秒")
    print("相关资料:")
    print("-" * 60)
    
    if not result.artifacts:
        print("  没有找到相关资料")
        return
    
    for i, artifact in enumerate(result.artifacts, 1):
        similarity = artifact.get('similarity', 0)
        title = artifact.get('title', '无标题')
        content = artifact.get('content', '')
        category = artifact.get('category', '未分类')
        
        print(f"\n{i}. {title}")
        print(f"   相似度: {similarity:.2f}")
        print(f"   分类: {category}")
        
        # 显示内容预览（前150个字符）
        if content:
            preview = content[:150]
            if len(content) > 150:
                preview += "..."
            print(f"   内容: {preview}")
    
    print("-" * 60)


def print_error(message):
    """打印错误信息
    
    Args:
        message: 错误信息
    """
    print(f"\n错误: {message}")
    print("请检查服务器状态或网络连接后重试")


def main():
    """主函数"""
    print_header()
    
    # 创建客户端实例
    try:
        client = SemanticRetrievalClient(
            base_url="http://localhost:8080/api/v1",
            timeout=300  # 5分钟超时
        )
        print("客户端初始化成功，已连接到服务器")
        print("服务器地址: http://localhost:8080/api/v1")
    except Exception as e:
        print(f"客户端初始化失败: {e}")
        print("请确保服务器正在运行，然后重新启动程序")
        print_footer()
        return
    
    # 交互式循环
    while True:
        try:
            # 读取用户输入
            user_input = input("\n请输入检索内容: ").strip()
            
            # 检查是否退出
            if user_input.lower() == 'exit':
                break
            
            # 检查输入是否为空
            if not user_input:
                print("输入不能为空，请重新输入")
                continue
            
            # 显示正在处理
            print(f"\n正在检索: '{user_input}'")
            print("等待服务器响应...")
            
            # 发送检索请求
            search_result = client.search(
                query=user_input,
                top_k=20,
                threshold=0.5
            )
            
            # 显示结果
            print_search_result(search_result)
            
        except KeyboardInterrupt:
            # 处理 Ctrl+C 中断
            print("\n用户中断操作")
            break
        except APIError as e:
            # 处理 API 错误
            print_error(f"API 错误: {e.status_code} - {e.message}")
        except ConnectionError as e:
            # 处理连接错误
            print_error(f"连接错误: {e}")
        except TimeoutError as e:
            # 处理超时错误
            print_error(f"超时错误: {e}")
        except Exception as e:
            # 处理其他错误
            print_error(f"未知错误: {e}")
    
    print_footer()


if __name__ == "__main__":
    main()
