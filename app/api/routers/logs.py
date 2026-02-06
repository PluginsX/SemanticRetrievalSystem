"""日志管理API路由"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List
from pathlib import Path
import json

router = APIRouter(prefix="/api/v1", tags=["日志管理"])


@router.get("/logs/database")
async def get_database_logs(lines: int = 100):
    """获取数据库日志"""
    log_file = Path("./logs/Database.log")
    
    if not log_file.exists():
        return {"logs": []}
    
    try:
        with open(log_file, 'r', encoding='utf-8-sig') as f:
            all_lines = f.readlines()
        
        # 获取最新的指定行数
        recent_lines = all_lines[-lines:] if len(all_lines) >= lines else all_lines
        logs = [line.strip() for line in recent_lines if line.strip()]
        
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取数据库日志失败: {str(e)}")


@router.get("/logs/server")
async def get_server_logs(lines: int = 100):
    """获取服务器日志"""
    log_file = Path("./logs/Server.log")
    
    if not log_file.exists():
        return {"logs": []}
    
    try:
        with open(log_file, 'r', encoding='utf-8-sig') as f:
            all_lines = f.readlines()
        
        # 获取最新的指定行数
        recent_lines = all_lines[-lines:] if len(all_lines) >= lines else all_lines
        logs = [line.strip() for line in recent_lines if line.strip()]
        
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取服务器日志失败: {str(e)}")


@router.delete("/logs/database")
async def clear_database_logs():
    """清空数据库日志"""
    log_file = Path("./logs/Database.log")
    
    try:
        # 确保logs目录存在
        log_file.parent.mkdir(exist_ok=True)
        
        # 直接清空文件内容
        with open(log_file, 'w', encoding='utf-8-sig') as f:
            f.write("")
        
        return {"message": "数据库日志已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空数据库日志失败: {str(e)}")


@router.delete("/logs/server")
async def clear_server_logs():
    """清空服务器日志"""
    log_file = Path("./logs/Server.log")
    
    try:
        # 确保logs目录存在
        log_file.parent.mkdir(exist_ok=True)
        
        # 直接清空文件内容
        with open(log_file, 'w', encoding='utf-8-sig') as f:
            f.write("")
        
        return {"message": "服务器日志已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空服务器日志失败: {str(e)}")


@router.get("/logs")
async def get_all_logs(lines: int = 100):
    """获取所有日志"""
    db_logs = []
    server_logs = []
    
    # 获取数据库日志
    db_log_file = Path("./logs/Database.log")
    if db_log_file.exists():
        try:
            with open(db_log_file, 'r', encoding='utf-8-sig') as f:
                all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) >= lines else all_lines
            db_logs = [line.strip() for line in recent_lines if line.strip()]
        except:
            pass
    
    # 获取服务器日志
    server_log_file = Path("./logs/Server.log")
    if server_log_file.exists():
        try:
            with open(server_log_file, 'r', encoding='utf-8-sig') as f:
                all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) >= lines else all_lines
            server_logs = [line.strip() for line in recent_lines if line.strip()]
        except:
            pass
    
    return {
        "database_logs": db_logs,
        "server_logs": server_logs
    }