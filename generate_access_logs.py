#!/usr/bin/env python3
"""
生成API访问日志测试数据
用于填充api_access_logs表，生成最近3个月的虚拟访问数据
"""
import sqlite3
import random
import datetime
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sqlite", "semantic_retrieval.db")

# 确保数据库目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# API端点列表
API_ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/metrics",
    "/api/v1/info",
    "/api/v1/reindex",
    "/api/v1/artifacts",
    "/api/v1/artifacts/search",
    "/api/v1/search",
    "/api/v1/config",
    "/api/v1/logs",
    "/api/v1/database/sqlite",
    "/api/v1/database/chromadb"
]

# HTTP方法列表
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"]

# 响应状态码列表
RESPONSE_STATUS = [200, 201, 204, 400, 401, 403, 404, 500]

# 客户端IP列表
CLIENT_IPS = [
    "192.168.1.1", "192.168.1.2", "192.168.1.3",
    "10.0.0.1", "10.0.0.2", "172.16.0.1",
    "127.0.0.1", "192.168.0.1", "192.168.0.2"
]

# 用户代理列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "PostmanRuntime/7.28.4",
    "curl/7.77.0",
    "python-requests/2.26.0"
]

def generate_access_logs(days=90, logs_per_day=50):
    """生成访问日志数据"""
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 确保表存在
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method VARCHAR(10) NOT NULL,
                client_ip TEXT,
                user_agent TEXT,
                response_status INTEGER,
                response_time FLOAT,
                created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        """)
        
        # 清除现有数据
        cursor.execute("DELETE FROM api_access_logs")
        print("已清除现有访问日志数据")
        
        # 生成数据
        total_logs = 0
        end_date = datetime.datetime.now()
        
        for day in range(days):
            current_date = end_date - datetime.timedelta(days=day)
            
            # 每天生成随机数量的日志（30-70条）
            daily_logs = random.randint(int(logs_per_day * 0.6), int(logs_per_day * 1.4))
            
            for _ in range(daily_logs):
                # 随机时间
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                log_time = current_date.replace(
                    hour=hour, 
                    minute=minute, 
                    second=second
                )
                
                # 随机数据
                endpoint = random.choice(API_ENDPOINTS)
                method = random.choice(HTTP_METHODS)
                client_ip = random.choice(CLIENT_IPS)
                user_agent = random.choice(USER_AGENTS)
                response_status = random.choice(RESPONSE_STATUS)
                response_time = round(random.uniform(0.1, 3.0), 3)
                
                # 插入数据
                cursor.execute(
                    """
                    INSERT INTO api_access_logs 
                    (endpoint, method, client_ip, user_agent, response_status, response_time, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (endpoint, method, client_ip, user_agent, response_status, response_time, 
                     log_time.strftime('%Y-%m-%d %H:%M:%S'))
                )
                
                total_logs += 1
        
        # 提交事务
        conn.commit()
        print(f"成功生成 {total_logs} 条访问日志数据")
        print(f"数据覆盖时间范围：{end_date - datetime.timedelta(days=days-1)} 到 {end_date}")
        
    except Exception as e:
        print(f"生成数据失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """主函数"""
    print("开始生成API访问日志测试数据...")
    generate_access_logs(days=90, logs_per_day=50)
    print("测试数据生成完成！")

if __name__ == "__main__":
    main()
