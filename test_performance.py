import time
import sqlite3
import datetime

def test_current_implementation():
    """测试当前实现的性能"""
    conn = sqlite3.connect(r"E:\Project\Python\SemanticRetrievalSystem\data\sqlite\semantic_retrieval.db")
    cursor = conn.cursor()
    
    days = 90
    
    # 计算开始日期
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    print(f"测试当前实现 - 查询过去 {days} 天的数据")
    
    # 记录查询开始时间
    query_start = time.time()
    
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
    query_end = time.time()
    
    print(f"SQL查询耗时: {query_end - query_start:.3f}秒")
    print(f"查询结果条数: {len(results)}")
    
    # 构建日期到访问量的映射
    stats_map = {row[0]: row[1] for row in results}
    
    # 记录数据处理开始时间
    processing_start = time.time()
    
    # 生成完整的日期范围
    date_list = []
    count_list = []
    
    for i in range(days):
        current_date = (start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        date_list.append(current_date)
        count_list.append(stats_map.get(current_date, 0))
    
    processing_end = time.time()
    
    print(f"数据处理耗时: {processing_end - processing_start:.3f}秒")
    print(f"总计耗时: {processing_end - query_start:.3f}秒")
    
    conn.close()

def test_optimized_implementation():
    """测试优化后的实现性能"""
    conn = sqlite3.connect(r"E:\Project\Python\SemanticRetrievalSystem\data\sqlite\semantic_retrieval.db")
    cursor = conn.cursor()
    
    days = 90
    
    # 计算开始日期
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    print(f"\n测试优化实现 - 查询过去 {days} 天的数据")
    
    # 记录查询开始时间
    query_start = time.time()
    
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
    query_end = time.time()
    
    print(f"SQL查询耗时: {query_end - query_start:.3f}秒")
    print(f"查询结果条数: {len(results)}")
    
    # 构建日期到访问量的映射（使用集合加快查找）
    stats_map = {row[0]: row[1] for row in results}
    
    # 记录数据处理开始时间
    processing_start = time.time()
    
    # 一次性生成所有日期，然后批量处理
    date_list = []
    count_list = []
    
    # 使用列表推导式一次性生成所有日期
    all_dates = [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    
    # 批量构建结果列表
    date_list = all_dates
    count_list = [stats_map.get(date, 0) for date in all_dates]
    
    processing_end = time.time()
    
    print(f"数据处理耗时: {processing_end - processing_start:.3f}秒")
    print(f"总计耗时: {processing_end - query_start:.3f}秒")
    
    conn.close()

if __name__ == "__main__":
    test_current_implementation()
    test_optimized_implementation()