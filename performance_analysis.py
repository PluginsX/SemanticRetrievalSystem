import time
import sqlite3
import datetime
import asyncio
import aiohttp

async def measure_api_response_time(session, url):
    """测量API响应时间"""
    start_time = time.time()
    try:
        async with session.get(url) as response:
            data = await response.json()
            end_time = time.time()
            return end_time - start_time, len(data.get('data', {}).get('dates', []))
    except Exception as e:
        end_time = time.time()
        return end_time - start_time, 0

async def analyze_performance():
    """分析性能瓶颈"""
    print("=== 性能分析开始 ===\n")
    
    # 1. 数据库查询性能测试
    print("1. 数据库查询性能测试:")
    conn = sqlite3.connect(r"E:\Project\Python\SemanticRetrievalSystem\data\sqlite\semantic_retrieval.db")
    cursor = conn.cursor()
    
    # 测试不同时间范围的查询性能
    for days in [7, 30, 90]:
        start_time = time.time()
        
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
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
        
        end_time = time.time()
        print(f"   {days}天查询: {end_time - start_time:.4f}秒, 结果: {len(results)}条")
    
    conn.close()
    
    # 2. API响应时间测试
    print("\n2. API响应时间测试:")
    
    async with aiohttp.ClientSession() as session:
        for days in [7, 30, 90]:
            url = f"http://localhost:12315/api/v1/access-stats?days={days}"
            response_time, data_points = await measure_api_response_time(session, url)
            print(f"   {days}天API响应: {response_time:.4f}秒, 数据点: {data_points}个")
    
    # 3. 数据处理算法性能测试
    print("\n3. 数据处理算法性能测试:")
    
    # 测试当前实现
    days = 90
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # 模拟查询结果
    mock_results = [((start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d'), i+10) for i in range(60)]  # 60天有数据
    stats_map = {row[0]: row[1] for row in mock_results}
    
    # 当前实现（循环方式）
    start_time = time.time()
    date_list = []
    count_list = []
    for i in range(days):
        current_date = (start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        date_list.append(current_date)
        count_list.append(stats_map.get(current_date, 0))
    current_time = time.time() - start_time
    print(f"   当前实现(90天): {current_time:.6f}秒")
    
    # 优化实现（批量处理）
    start_time = time.time()
    all_dates = [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    optimized_date_list = all_dates
    optimized_count_list = [stats_map.get(date, 0) for date in all_dates]
    optimized_time = time.time() - start_time
    print(f"   优化实现(90天): {optimized_time:.6f}秒")
    
    print(f"   性能提升: {(current_time / optimized_time) if optimized_time > 0 else float('inf'):.2f}倍")
    
    # 4. 数据量统计
    print("\n4. 数据量统计:")
    conn = sqlite3.connect(r"E:\Project\Python\SemanticRetrievalSystem\data\sqlite\semantic_retrieval.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM api_access_logs")
    total_records = cursor.fetchone()[0]
    
    # 统计最近90天的记录
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=90)
    cursor.execute("SELECT COUNT(*) FROM api_access_logs WHERE created_at >= ?", (start_date.strftime('%Y-%m-%d'),))
    recent_90_days = cursor.fetchone()[0]
    
    # 统计最近30天的记录
    start_date = end_date - datetime.timedelta(days=30)
    cursor.execute("SELECT COUNT(*) FROM api_access_logs WHERE created_at >= ?", (start_date.strftime('%Y-%m-%d'),))
    recent_30_days = cursor.fetchone()[0]
    
    # 统计最近7天的记录
    start_date = end_date - datetime.timedelta(days=7)
    cursor.execute("SELECT COUNT(*) FROM api_access_logs WHERE created_at >= ?", (start_date.strftime('%Y-%m-%d'),))
    recent_7_days = cursor.fetchone()[0]
    
    print(f"   总记录数: {total_records}")
    print(f"   最近90天: {recent_90_days}")
    print(f"   最近30天: {recent_30_days}")
    print(f"   最近7天: {recent_7_days}")
    
    conn.close()
    
    print("\n=== 性能分析完成 ===")

if __name__ == "__main__":
    asyncio.run(analyze_performance())