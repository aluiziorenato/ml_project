import redis
import json
import logging

# Configuração do logger
logging.basicConfig(filename='learning_service_integration.log', level=logging.INFO)

# Configuração do Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Função para publicar eventos

def publish_event(event_type, details):
    event = {
        "type": event_type,
        "timestamp": "2025-08-30T12:00:00Z",
        "details": details
    }
    r.publish('learning_events', json.dumps(event))
    logging.info(f"Evento publicado: {event}")

# Exemplo de uso
if __name__ == "__main__":
    publish_event("anomaly", {"score": 0.98, "feature": "latency"})
    publish_event("recommendation", {"action": "increase_bid", "product_id": 12345})
    publish_event("alert", {"message": "Competitor campaign detected", "severity": "high"})
