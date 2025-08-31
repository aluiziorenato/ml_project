import unittest
import redis
import json
from src.api import user_strategy

class TestUserStrategyAPI(unittest.TestCase):
    def setUp(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.redis.flushdb()

    def test_publish_user_strategy_selection(self):
        event = {
            "type": "user_strategy_selection",
            "timestamp": "2025-08-30T12:00:00Z",
            "details": {"strategy": "competitivo", "parameters": {"budget": 1000}}
        }
        self.redis.publish('user_strategy_events', json.dumps(event))
        pubsub = self.redis.pubsub()
        pubsub.subscribe('user_strategy_events')
        message = next(pubsub.listen())
        if message['type'] == 'message':
            received_event = json.loads(message['data'])
            self.assertEqual(received_event['type'], "user_strategy_selection")
            self.assertEqual(received_event['details']['strategy'], "competitivo")

if __name__ == "__main__":
    unittest.main()
