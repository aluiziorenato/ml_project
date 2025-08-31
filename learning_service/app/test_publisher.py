import unittest
import redis
import json
from app import publisher

class TestLearningServicePublisher(unittest.TestCase):
    def setUp(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.redis.flushdb()

    def test_publish_anomaly_event(self):
        publisher.publish_event("anomaly", {"score": 0.99, "feature": "latency"})
        pubsub = self.redis.pubsub()
        pubsub.subscribe('learning_events')
        message = next(pubsub.listen())
        if message['type'] == 'message':
            event = json.loads(message['data'])
            self.assertEqual(event['type'], "anomaly")
            self.assertIn("score", event['details'])

    def test_publish_recommendation_event(self):
        publisher.publish_event("recommendation", {"action": "increase_bid", "product_id": 12345})
        pubsub = self.redis.pubsub()
        pubsub.subscribe('learning_events')
        message = next(pubsub.listen())
        if message['type'] == 'message':
            event = json.loads(message['data'])
            self.assertEqual(event['type'], "recommendation")
            self.assertIn("action", event['details'])

if __name__ == "__main__":
    unittest.main()
