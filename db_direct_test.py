import time
import sqlite3
import datetime

# 直接测试数据库查询性能
def test_direct_db_query():
    start_time = time.time()
    
    conn = sqlite3.connect(r"E:\Project\Python\SemanticRetrievalSystem\data\sqlite\semantic_retrieval.db")
    cursor = conn.cursor()
    
    days = 90
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # 按日期分组统计访问量
    cursor.execute("""
        SELECT 
            DATE(created_at) as date, 
            COUNT(*) as count
        FROM 
            api_access_logs
        WHERE 
            created_at >= ?
        GROUP BY 
            DATE(created_at)
        ORDER BY 
            date
    """, (start_date.strftime('%Y-%m-%d'),))
    
    results = cursor.fetchall()
    
    # 生成完整的日期范围（优化：使用列表推导式一次性生成所有日期）
    base_date = start_date.date()  # 转换为date类型以提高性能
    all_dates = [(base_date + datetime.timedelta(days=i)).isoformat() for i in range(days)]
    date_list = all_dates
    count_list = [dict(results).get(date, 0) for date in all_dates]
    
    # 优化：在同一次遍历中计算总和，避免多次遍历
    total = sum(count_list)
    average = total / days if days > 0 else 0
    
    conn.close()
    
    end_time = time.time()
    print(f"直接数据库查询耗时: {(end_time - start_time)*1000:.2f}ms")
    print(f"结果数量: {len(date_list)}")
    print(f"总访问量: {total}")

if __name__ == "__main__":
    # 运行多次测试平均值
    times = []
    for i in range(10):
        start_time = time.time()
        
        conn = sqlite3.connect(r"E:\Project\Python\SemanticRetrievalSystem\data\sqlite\semantic_retrieval.db")
        cursor = conn.cursor()
        
        days = 90
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        # 按日期分组统计访问量
        cursor.execute("""
            SELECT 
                DATE(created_at) as date, 
                COUNT(*) as count
            FROM 
                api_access_logs
            WHERE 
                created_at >= ?
            GROUP BY 
                DATE(created_at)
            ORDER BY 
                date
        """, (start_date.strftime('%Y-%m-%d'),))
        
        results = cursor.fetchall()
        
        # 生成完整的日期范围（优化：使用列表推导式一次性生成所有日期）
        base_date = start_date.date()  # 转换为date类型以提高性能
        all_dates = [(base_date + datetime.timedelta(days=i)).isoformat() for i in range(days)]
        date_list = all_dates
        count_list = [dict(results).get(date, 0) for date in all_dates]
        
        # 优化：在同一次遍历中计算总和，避免多次遍历
        total = sum(count_list)
        average = total / days if days > 0 else 0
        
        conn.close()
        
        end_time = time.time()
        times.append((end_time - start_time) * 1000)  # 转换为毫秒
    
    avg_time = sum(times) / len(times)
    print(f"平均耗时: {avg_time:.2f}ms")
    print(f"最短耗时: {min(times):.2f}ms")
    print(f"最长耗时: {max(times):.2f}ms")