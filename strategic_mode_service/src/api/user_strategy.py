from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import redis
import json
import logging

router = APIRouter()

# Configuração do logger
logging.basicConfig(filename='strategic_mode_service_api.log', level=logging.INFO)

# Configuração do Redis
r = redis.Redis(host='localhost', port=6379, db=0)

class StrategySelection(BaseModel):
    strategy: str
    parameters: dict = {}

@router.post("/select-strategy")
def select_strategy(selection: StrategySelection):
    # Publica a escolha do usuário em um canal Redis
    event = {
        "type": "user_strategy_selection",
        "timestamp": "2025-08-30T12:00:00Z",
        "details": {
            "strategy": selection.strategy,
            "parameters": selection.parameters
        }
    }
    r.publish('user_strategy_events', json.dumps(event))
    logging.info(f"Usuário selecionou estratégia: {event}")
    return {"status": "success", "event": event}
