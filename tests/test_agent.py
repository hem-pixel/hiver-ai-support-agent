import unittest
from app.agent import SupportAgent
from app.models import AgentOutput


class TestSupportAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.agent = SupportAgent()

    def test_full_pipeline_fare_charge(self):
        msg = "I was charged too much for my Uber ride and want a refund"
        output = self.agent.process(msg)

        self.assertIsInstance(output, AgentOutput)
        self.assertEqual(output.customer_message, msg)
        self.assertIn(output.intent, ["fare_or_charge_issue", "refund_request"])
        self.assertIsNotNone(output.retrieval)
        self.assertIn(output.action, ["AUTO_HANDLE", "ESCALATE"])
        self.assertTrue(len(output.draft_reply) > 0)
        self.assertTrue(len(output.reason) > 0)

        # Test dictionary serialization
        out_dict = output.to_dict()
        self.assertEqual(out_dict["customer_message"], msg)
        self.assertIn("action", out_dict)
        self.assertIn("reason", out_dict)

    def test_full_pipeline_uber_eats(self):
        msg = "My food delivery was completely wrong and items were missing from the order"
        output = self.agent.process(msg)

        self.assertEqual(output.intent, "uber_eats_issue")
        self.assertIsNotNone(output.retrieval)
        self.assertTrue(len(output.draft_reply) > 0)


if __name__ == "__main__":
    unittest.main()
