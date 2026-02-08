"""
语义检索系统主应用入口
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.core.config import config
from app.core.database import db_manager
from app.api.routers import system, artifacts, search, logs, database
from app.api.routers import config as config_router
from app.core.config_hot_reload import set_fastapi_app, set_config_instance, register_config_change_listener

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定义lifespan事件处理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器"""
    # 启动事件
    logger.info("正在启动语义检索系统...")
    
    # 初始化数据库连接
    try:
        db_manager.init_sqlite()
        chroma_result = db_manager.init_chroma()
        if chroma_result is None and db_manager.chroma_available:
            logger.warning("ChromaDB初始化失败，但标记为可用")
        elif not db_manager.chroma_available:
            logger.warning("ChromaDB不可用，向量搜索功能将被禁用")
        else:
            logger.info("ChromaDB初始化完成")
        logger.info("数据库连接初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    
    logger.info(f"语义检索系统启动完成，监听地址: http://localhost:{config.PORT}")
    
    # 自动打开默认浏览器访问控制面板
    import webbrowser
    import threading
    
    def open_browser():
        """在新线程中打开浏览器，避免阻塞服务启动"""
        try:
            control_panel_url = f"http://localhost:{config.PORT}"
            logger.info(f"正在打开控制面板: {control_panel_url}")
            webbrowser.open(control_panel_url)
        except Exception as e:
            logger.warning(f"自动打开浏览器失败: {e}")
    
    # 在新线程中执行，避免阻塞服务
    threading.Thread(target=open_browser, daemon=True).start()
    
    yield  # 应用运行期间
    
    # 关闭事件
    logger.info("正在关闭语义检索系统...")
    db_manager.close_connections()
    logger.info("语义检索系统已关闭")

# 创建FastAPI应用
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    debug=config.DEBUG,
    lifespan=lifespan
)

# 注册API路由
app.include_router(system.router)
app.include_router(artifacts.router)
app.include_router(search.router)
app.include_router(config_router.router)
app.include_router(logs.router)
app.include_router(database.router)

# 添加CORS中间件
if config.WEB_SERVICE_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 存储CORS中间件配置以便后续更新
cors_origins = config.ALLOWED_ORIGINS

# 设置热重载相关实例
set_fastapi_app(app)
set_config_instance(config)

# 注册配置变更监听器
register_config_change_listener()

# API欢迎信息
@app.get("/api")
async def api_root():
    """API根路径欢迎页面"""
    return {
        "message": f"欢迎使用{config.APP_NAME}",
        "version": config.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "vector_store": "connected",
            "llm_service": "configured",
            "embedding_service": "configured"
        }
    }

# 挂载静态文件
if config.WEB_SERVICE_ENABLED:
    import os
    static_dir = config.STATIC_FILES_DIR
    if os.path.exists(static_dir):
        # 挂载静态文件到/static路径
        app.mount(config.STATIC_MOUNT_PATH, StaticFiles(directory=static_dir), name="static")
        
        # 为前端单页应用提供服务
        from fastapi.responses import FileResponse
        
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """为前端单页应用提供服务"""
            # 如果请求的是API路径或其他系统路径，则跳过
            if (full_path.startswith("api/") or 
                full_path.startswith("docs") or 
                full_path.startswith("redoc") or 
                full_path.startswith("openapi.json") or
                full_path == "api" or
                full_path == "health"):
                # 让FastAPI处理这些路径
                return None
            
            # 否则提供前端静态文件
            file_path = os.path.join(static_dir, full_path)
            index_path = os.path.join(static_dir, "index.html")
            
            # 如果文件存在且不是目录，则提供该文件
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            
            # 否则提供index.html（SPA路由）
            return FileResponse(index_path)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )