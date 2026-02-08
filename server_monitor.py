import os
import sys
import time
import subprocess
import psutil
import argparse

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="服务器监控脚本")
    parser.add_argument("--pid", type=int, required=True, help="服务器进程ID")
    parser.add_argument("--mode", type=str, choices=["restart", "shutdown"], default="restart", help="操作模式")
    parser.add_argument("--start-bat", type=str, help="启动脚本路径")
    return parser.parse_args()

def kill_server_process(pid):
    """终止服务器进程"""
    print(f"开始终止服务器进程: {pid}")
    
    # 找到所有相关进程
    process_ids = [pid]
    
    # 获取进程对象
    try:
        target_process = psutil.Process(pid)
        
        # 添加子进程
        for child in target_process.children(recursive=True):
            process_ids.append(child.pid)
        
        # 添加父进程（如果是python或uvicorn进程）
        if target_process.parent() is not None:
            parent = target_process.parent()
            if 'python' in parent.name().lower() or 'uvicorn' in parent.name().lower():
                process_ids.append(parent.pid)
        
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        print(f"无法获取进程信息: {pid}")
    
    # 去重
    process_ids = list(set(process_ids))
    print(f"找到相关进程: {process_ids}")
    
    # 终止所有相关进程
    for pid_to_kill in process_ids:
        try:
            proc = psutil.Process(pid_to_kill)
            print(f"终止进程: {pid_to_kill} ({proc.name()})")
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"无法终止进程: {pid_to_kill}")
    
    # 等待进程终止
    time.sleep(1)
    
    # 强制终止仍在运行的进程
    for pid_to_kill in process_ids:
        try:
            proc = psutil.Process(pid_to_kill)
            if proc.is_running():
                print(f"强制终止进程: {pid_to_kill}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    print("进程终止操作完成")

def start_server(start_bat):
    """启动服务器"""
    print(f"启动服务器，脚本: {start_bat}")
    try:
        # 启动服务器
        subprocess.Popen(
            start_bat,
            shell=True,
            cwd=os.path.dirname(start_bat),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print("服务器启动成功")
        return True
    except Exception as e:
        print(f"启动服务器失败: {e}")
        return False

def main():
    """监控脚本主逻辑"""
    args = parse_args()
    server_pid = args.pid
    mode = args.mode
    start_bat = args.start_bat
    
    print(f"监控脚本已启动，模式: {mode}")
    print(f"目标进程 PID: {server_pid}")
    if start_bat:
        print(f"启动脚本: {start_bat}")
    
    # 终止服务器进程
    kill_server_process(server_pid)
    
    # 如果是重启模式，则启动服务器
    if mode == "restart" and start_bat:
        print("等待1秒后启动服务器...")
        time.sleep(1)
        print("准备启动服务器...")
        if start_server(start_bat):
            print("服务器已启动，监控脚本退出")
        else:
            print("服务器启动失败，监控脚本退出")
    else:
        print("关闭模式，监控脚本退出")

if __name__ == "__main__":
    main()