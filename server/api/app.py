"""
FastAPI 应用 - API 网关
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="StyleWriter API",
    description="风格化文章生成服务",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 Agent 实例
agent = None

class GenerateRequest(BaseModel):
    topic: str
    length: int = 1000
    requirements: str = ""
    style: str = "default"
    use_model: str = "api"  # "api" or "local"

class GenerateResponse(BaseModel):
    content: str
    word_count: int
    style_score: float
    model_used: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

@app.on_event("startup")
async def startup():
    """启动时初始化"""
    global agent
    from server.agent.hybrid_agent import HybridAgent
    agent = HybridAgent()
    agent.initialize()
    logger.info("Agent 初始化完成")

@app.get("/")
async def root():
    return {"message": "StyleWriter API", "version": "1.0.0"}

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_article(request: GenerateRequest):
    """生成文章"""
    try:
        result = agent.generate(
            topic=request.topic,
            length=request.length,
            requirements=request.requirements,
            style=request.style,
            use_model=request.use_model
        )
        return GenerateResponse(
            content=result["content"],
            word_count=result["word_count"],
            style_score=result["style_score"],
            model_used=result["model_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_references(request: SearchRequest):
    """检索参考文章"""
    try:
        results = agent.search(request.query, request.top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """获取服务状态"""
    return {
        "status": "running",
        "agent_initialized": agent is not None,
        "local_model_loaded": agent.local_model is not None if agent else False,
        "api_configured": agent.api_configured if agent else False
    }

@app.post("/api/reload")
async def reload_agent():
    """重新加载 Agent"""
    try:
        agent.reload()
        return {"message": "Agent 重新加载成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

