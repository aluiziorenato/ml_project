import unittest
import redis
import json
import time

class TestEventConsumerResilience(unittest.TestCase):
    def setUp(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.redis.flushdb()

    def test_consume_event_with_redis_failure(self):
        # Simula publicação de evento
        event = {
            "type": "anomaly",
            "timestamp": "2025-08-30T12:00:00Z",
            "details": {"score": 0.98, "feature": "latency"}
        }
        self.redis.publish('learning_events', json.dumps(event))
        # Simula falha temporária do Redis (desconexão)
        try:
            self.redis.connection_pool.disconnect()
            time.sleep(1)  # Tempo para simular indisponibilidade
        except Exception:
            pass
        # Reconecta e verifica se evento pode ser consumido após falha
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        pubsub = self.redis.pubsub()
        pubsub.subscribe('learning_events')
        message = next(pubsub.listen())
        if message['type'] == 'message':
            received_event = json.loads(message['data'])
            self.assertEqual(received_event['type'], "anomaly")

    def test_consume_multiple_events_overload(self):
        # Simula sobrecarga de eventos
        for i in range(100):
            event = {
                "type": "anomaly",
                "timestamp": f"2025-08-30T12:00:{i:02d}Z",
                "details": {"score": 0.90 + i*0.001, "feature": "latency"}
            }
            self.redis.publish('learning_events', json.dumps(event))
        pubsub = self.redis.pubsub()
        pubsub.subscribe('learning_events')
        count = 0
        for message in pubsub.listen():
            if message['type'] == 'message':
                count += 1
            if count == 100:
                break
        self.assertEqual(count, 100)

if __name__ == "__main__":
    unittest.main()
