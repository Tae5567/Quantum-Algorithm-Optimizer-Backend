from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import router
from src.config import settings

app = FastAPI(
    title="Quantum Optimizer - Multi-Agent System",
    description="""
    AI-powered algorithm recommendation engine using autonomous multi-agent architecture.
    
    **Agent System:**
    - 🧠 Complexity Analyzer: Analyzes computational complexity
    - 💰 Cost Estimator: Calculates ROI and cost comparisons
    - ⚛️ Quantum Feasibility: Assesses quantum hardware requirements
    - 🎯 Decision Maker: Synthesizes inputs and recommends approach
    
    **Powered by:**
    - AWS Bedrock Nova Pro (Multi-Agent AI)
    - AWS Braket (Quantum Computing)
    - LangChain (Agent Orchestration)
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["multi-agent-system"])

@app.get("/")
async def root():
    return {
        "service": "Quantum Optimizer Multi-Agent System",
        "version": "2.0.0",
        "description": "AI-powered algorithm recommendation using autonomous agents",
        "architecture": "multi-agent-orchestration",
        "agents": 4,
        "powered_by": [
            "AWS Bedrock Nova Pro",
            "AWS Braket",
            "LangChain"
        ],
        "endpoints": {
            "analyze": "/api/v1/analyze/multi-agent",
            "agents": "/api/v1/agents/info",
            "playground": "/api/v1/playground/run/{problem_id}",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )