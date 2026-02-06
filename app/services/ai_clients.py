"""
AI服务客户端模块
包含LLM和Embedding服务的客户端实现
"""
import asyncio
from typing import List, Optional, Dict, Any
import openai
from openai import AsyncOpenAI
import logging

from ..core.config import config

logger = logging.getLogger(__name__)


class LLMClient:
    """大语言模型客户端"""
    
    def __init__(self):
        """初始化LLM客户端"""
        self.client = AsyncOpenAI(
            base_url=config.LLM_API_BASE_URL,
            api_key=config.LLM_API_KEY,
            timeout=config.LLM_TIMEOUT
        )
        self.model = config.LLM_MODEL
        self.max_retries = config.LLM_MAX_RETRIES if hasattr(config, 'LLM_MAX_RETRIES') else 3
        logger.info(f"LLM客户端初始化完成，模型: {self.model}")
    
    async def generate_summary(self, text: str, max_tokens: int = 300) -> str:
        """
        生成文本摘要
        
        Args:
            text: 输入文本
            max_tokens: 最大token数
            
        Returns:
            生成的摘要文本
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一个专业的资料分析助手，请为用户提供简洁准确的摘要"
                    },
                    {
                        "role": "user", 
                        "content": f"请为以下资料生成摘要（{max_tokens}字以内）：\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"生成摘要失败: {str(e)}")
            raise
    
    async def extract_metadata(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取元数据
        
        Args:
            text: 输入文本
            
        Returns:
            提取的元数据字典
        """
        try:
            prompt = f"""
            请从以下文本中提取相关的元数据信息，以JSON格式返回：
            
            文本内容：
            {text[:2000]}  # 限制长度避免超出上下文窗口
            
            请提取以下可能的信息：
            - title: 标题
            - author: 作者
            - date: 日期
            - category: 分类
            - keywords: 关键词列表
            
            只返回有效的JSON对象，不要包含其他解释文字。
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一个专业的元数据提取助手，只返回JSON格式的结果"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"提取元数据失败: {str(e)}")
            return {}
    
    async def answer_question(self, query: str, context: str) -> str:
        """
        基于上下文回答问题
        
        Args:
            query: 用户问题
            context: 相关上下文
            
        Returns:
            回答内容
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一个专业的知识问答助手，请基于提供的资料准确回答用户问题"
                    },
                    {
                        "role": "user", 
                        "content": f"参考资料：\n{context}\n\n问题：{query}"
                    }
                ],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"回答问题失败: {str(e)}")
            raise


class EmbeddingClient:
    """向量嵌入客户端"""
    
    def __init__(self):
        """初始化Embedding客户端"""
        self.client = AsyncOpenAI(
            base_url=config.EMBEDDING_API_BASE_URL,
            api_key=config.EMBEDDING_API_KEY,
            timeout=config.EMBEDDING_TIMEOUT
        )
        self.model = config.EMBEDDING_MODEL
        self.dimensions = config.EMBEDDING_DIMENSIONS
        self.max_retries = config.EMBEDDING_MAX_RETRIES if hasattr(config, 'EMBEDDING_MAX_RETRIES') else 3
        logger.info(f"Embedding客户端初始化完成，模型: {self.model}")
    
    async def embed(self, text: str) -> List[float]:
        """
        将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            向量表示（浮点数列表）
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"文本向量化失败: {str(e)}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量文本向量化
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        try:
            # 分批处理避免超出API限制
            batch_size = 10
            embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
            return embeddings
        except Exception as e:
            logger.error(f"批量向量化失败: {str(e)}")
            raise


# 全局客户端实例
llm_client = LLMClient()
embedding_client = EmbeddingClient()