"""日志管理API路由"""
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, List
from pathlib import Path as PathLib
import json

Path = Path
PathLib = PathLib

router = APIRouter(prefix="/api/v1", tags=["日志管理"])


log_file_map = {
    "database": "./logs/Database.log",
    "server": "./logs/Server.log"
}


@router.get("/logs/{log_type}")
async def get_logs(
    log_type: str = Path(..., description="日志类型", regex="^(database|server)$"),
    lines: int = 100
):
    """获取指定类型的日志"""
    if log_type not in log_file_map:
        raise HTTPException(status_code=400, detail="无效的日志类型")
    
    log_file = PathLib(log_file_map[log_type])
    
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
        raise HTTPException(status_code=500, detail=f"读取{log_type}日志失败: {str(e)}")


@router.delete("/logs/{log_type}")
async def clear_logs(
    log_type: str = Path(..., description="日志类型", regex="^(database|server)$")
):
    """清空指定类型的日志"""
    if log_type not in log_file_map:
        raise HTTPException(status_code=400, detail="无效的日志类型")
    
    log_file = PathLib(log_file_map[log_type])
    
    try:
        # 确保logs目录存在
        log_file.parent.mkdir(exist_ok=True)
        
        # 直接清空文件内容
        with open(log_file, 'w', encoding='utf-8-sig') as f:
            f.write("")
        
        return {"message": f"{log_type}日志已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空{log_type}日志失败: {str(e)}")


@router.get("/logs")
async def get_all_logs(lines: int = 100):
    """获取所有日志"""
    logs = {}
    
    for log_type, log_path in log_file_map.items():
        log_file = PathLib(log_path)
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8-sig') as f:
                    all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) >= lines else all_lines
                logs[f"{log_type}_logs"] = [line.strip() for line in recent_lines if line.strip()]
            except:
                logs[f"{log_type}_logs"] = []
        else:
            logs[f"{log_type}_logs"] = []
    
    return logs