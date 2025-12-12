from fastapi import FastAPI, Request
from app.api.routes import router
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Workflow Engine", version="1.0.0")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"→ {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    
    return response

app.include_router(router)

@app.get("/")
def root():
    return {"status": "running", "service": "workflow-engine"}
