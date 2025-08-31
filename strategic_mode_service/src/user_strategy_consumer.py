import redis
import json
import logging

# Configuração do logger
logging.basicConfig(filename='strategic_mode_service_user_strategy.log', level=logging.INFO)

# Configuração do Redis
r = redis.Redis(host='localhost', port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe('user_strategy_events')

# Função para processar escolhas do usuário
def process_user_strategy(event):
    strategy = event.get("details", {}).get("strategy")
    parameters = event.get("details", {}).get("parameters", {})
    logging.info(f"Estratégia selecionada pelo usuário: {strategy}, parâmetros: {parameters}")
    # Aqui pode-se aplicar lógica para ativar/desativar modos conforme escolha do usuário
    # Exemplo: ativar modo competitivo, defensivo, otimização, etc.

if __name__ == "__main__":
    for message in pubsub.listen():
        if message['type'] == 'message':
            event = json.loads(message['data'])
            process_user_strategy(event)
