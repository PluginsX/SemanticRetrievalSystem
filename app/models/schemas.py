"""
Pydantic数据模型定义
用于API请求和响应的数据验证
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ArtifactBase(BaseModel):
    """资料基础模型"""
    title: str = Field(..., description="资料标题", min_length=1, max_length=500)
    content: str = Field(..., description="资料内容", min_length=1)
    category: Optional[str] = Field(None, description="分类标签", max_length=64)
    tags: Optional[List[str]] = Field(None, description="标签列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class ArtifactCreate(ArtifactBase):
    """创建资料请求模型"""
    source_type: Optional[str] = Field(None, description="来源类型")
    source_path: Optional[str] = Field(None, description="来源路径")


class ArtifactUpdate(BaseModel):
    """更新资料请求模型"""
    title: Optional[str] = Field(None, description="资料标题", min_length=1, max_length=500)
    content: Optional[str] = Field(None, description="资料内容", min_length=1)
    category: Optional[str] = Field(None, description="分类标签", max_length=64)
    tags: Optional[List[str]] = Field(None, description="标签列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ChunkInfo(BaseModel):
    """切片信息模型"""
    chunk_id: int = Field(..., description="切片ID")
    content: str = Field(..., description="切片内容")
    similarity: Optional[float] = Field(None, description="相似度得分")
    chunk_index: int = Field(..., description="切片序号")


class ArtifactResponse(ArtifactBase):
    """资料响应模型"""
    id: int = Field(..., description="资料ID")
    source_type: Optional[str] = Field(None, description="来源类型")
    source_path: Optional[str] = Field(None, description="来源路径")
    similarity: Optional[float] = Field(None, description="相似度得分")
    chunks: Optional[List[ChunkInfo]] = Field(None, description="相关切片")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_active: bool = Field(..., description="是否激活")

    class Config:
        from_attributes = True


class ArtifactListResponse(BaseModel):
    """资料列表响应模型"""
    artifacts: List[ArtifactResponse] = Field(..., description="资料列表")
    total_count: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class SearchResult(ArtifactResponse):
    """检索结果模型"""
    pass


class SearchRequest(BaseModel):
    """检索请求模型"""
    query: str = Field(..., description="查询语句", min_length=1, max_length=1000)
    top_k: int = Field(5, description="返回结果数量", ge=1, le=100)
    threshold: float = Field(0.7, description="相似度阈值", ge=0.0, le=1.0)
    category_filter: Optional[List[str]] = Field(None, description="分类过滤")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="元数据过滤")


class SearchResponse(BaseModel):
    """检索响应模型"""
    query: str = Field(..., description="查询语句")
    artifacts: List[SearchResult] = Field(..., description="检索结果")
    total_count: int = Field(..., description="结果总数")
    response_time: float = Field(..., description="响应时间(秒)")


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
    services: Dict[str, str] = Field(..., description="各服务状态")


class MetricsResponse(BaseModel):
    """系统指标响应模型"""
    uptime: float = Field(..., description="运行时间(秒)")
    artifact_count: int = Field(..., description="资料总数")
    chunk_count: int = Field(..., description="切片总数")
    search_count: int = Field(..., description="检索次数")
    avg_response_time: float = Field(..., description="平均响应时间(秒)")


class BatchImportRequest(BaseModel):
    """批量导入请求模型"""
    files: List[str] = Field(..., description="文件路径列表")
    category: Optional[str] = Field(None, description="默认分类")
    recursive: bool = Field(False, description="是否递归处理子目录")


class ImportResult(BaseModel):
    """导入结果模型"""
    total_files: int = Field(..., description="总文件数")
    successful: int = Field(..., description="成功处理数")
    failed: int = Field(..., description="失败数")
    errors: List[str] = Field(..., description="错误信息列表")
    processing_time: float = Field(..., description="处理耗时(秒)")


# 数据库模型对应的Pydantic模型
class ArtifactInDB(ArtifactResponse):
    """数据库中的资料模型"""
    pass


class ChunkInDB(ChunkInfo):
    """数据库中的切片模型"""
    artifact_id: int = Field(..., description="所属资料ID")
    token_count: Optional[int] = Field(None, description="token数量")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class SearchHistoryInDB(BaseModel):
    """数据库中的检索历史模型"""
    id: int = Field(..., description="记录ID")
    query: str = Field(..., description="查询语句")
    artifact_count: Optional[int] = Field(None, description="返回资料数量")
    response_time: Optional[float] = Field(None, description="响应时间")
    user_agent: Optional[str] = Field(None, description="用户代理")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True