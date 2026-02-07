#!/usr/bin/env python3
"""
测试配置保存功能
"""
import os
import sys
import logging

# 设置日志级别为INFO，以便看到保存配置的日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.yaml_config import get_config_manager


def test_config_save():
    """测试配置保存功能"""
    print("=== 测试配置保存功能 ===")
    
    # 获取配置管理器实例
    config_manager = get_config_manager()
    print("✓ 获取配置管理器实例成功")
    
    # 获取当前配置
    current_config = config_manager.get_config()
    print(f"✓ 获取当前配置成功，配置项数量: {len(current_config)}")
    
    # 修改配置
    test_host = "192.168.1.100"
    test_port = 8888
    
    # 更新服务器配置
    if "app" not in current_config:
        current_config["app"] = {}
    
    current_config["app"]["host"] = test_host
    current_config["app"]["port"] = test_port
    
    print(f"✓ 修改配置成功，新的host: {test_host}, port: {test_port}")
    
    # 保存配置
    try:
        config_manager.update_config(current_config)
        print("✓ 保存配置成功")
        
        # 检查current_config.yaml文件是否存在
        config_path = os.path.join(os.path.dirname(__file__), "config", "current_config.yaml")
        if os.path.exists(config_path):
            print(f"✓ current_config.yaml文件已创建: {config_path}")
            
            # 读取文件内容，验证配置是否正确保存
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✓ 读取配置文件内容成功，文件大小: {len(content)} bytes")
                
                if test_host in content and str(test_port) in content:
                    print("✓ 配置值已正确保存到文件中")
                else:
                    print("✗ 配置值未正确保存到文件中")
        else:
            print("✗ current_config.yaml文件未创建")
            
    except Exception as e:
        print(f"✗ 保存配置失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_config_save()
