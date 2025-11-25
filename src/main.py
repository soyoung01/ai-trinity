from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.api.endpoints import health, fitness
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router, prefix="", tags=["Health"])
app.include_router(fitness.router, prefix=settings.API_V1_PREFIX + "/fitness", tags=["Fitness"])


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    logger.info("=" * 80)
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} 시작")
    logger.info("=" * 80)
    logger.info(f"API 문서: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"ReDoc: http://{settings.HOST}:{settings.PORT}/redoc")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행"""
    logger.info("서버를 종료합니다...")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "AI-TRINITY API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )