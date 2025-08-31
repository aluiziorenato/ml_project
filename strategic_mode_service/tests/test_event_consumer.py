import unittest
import redis
import json
from src import event_consumer

class TestStrategicModeEventConsumer(unittest.TestCase):
    def setUp(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.redis.flushdb()

    def test_consume_anomaly_event(self):
        event = {
            "type": "anomaly",
            "timestamp": "2025-08-30T12:00:00Z",
            "details": {"score": 0.98, "feature": "latency"}
        }
        self.redis.publish('learning_events', json.dumps(event))
        pubsub = self.redis.pubsub()
        pubsub.subscribe('learning_events')
        message = next(pubsub.listen())
        if message['type'] == 'message':
            received_event = json.loads(message['data'])
            self.assertEqual(received_event['type'], "anomaly")
            self.assertIn("score", received_event['details'])

    def test_consume_recommendation_event(self):
        event = {
            "type": "recommendation",
            "timestamp": "2025-08-30T12:00:00Z",
            "details": {"action": "increase_bid", "product_id": 12345}
        }
        self.redis.publish('learning_events', json.dumps(event))
        pubsub = self.redis.pubsub()
        pubsub.subscribe('learning_events')
        message = next(pubsub.listen())
        if message['type'] == 'message':
            received_event = json.loads(message['data'])
            self.assertEqual(received_event['type'], "recommendation")
            self.assertIn("action", received_event['details'])

if __name__ == "__main__":
    unittest.main()
