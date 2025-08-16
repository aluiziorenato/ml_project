"""
Market Pulse - Real-Time Market Pulse
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="Market Pulse - Real-Time SEO Intelligence",
    description="Real-time market monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "market_pulse",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/live-heatmap")
async def get_live_heatmap():
    return {
        "keywords": [
            {"keyword": "smartphone", "heat": 0.95, "volume": 15000},
            {"keyword": "laptop", "heat": 0.82, "volume": 8000}
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
