import unittest
from app.decision import DecisionEngine
from app.models import Action, Intent, RetrievalResult


class TestDecisionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DecisionEngine(similarity_threshold=0.20)

    def test_escalate_on_missing_retrieval(self):
        decision = self.engine.decide(Intent.FARE_OR_CHARGE_ISSUE.value, None)
        self.assertEqual(decision.action, Action.ESCALATE)
        self.assertIn("No historical resolution", decision.reason)

    def test_escalate_on_low_similarity(self):
        retrieval = RetrievalResult(
            intent=Intent.FARE_OR_CHARGE_ISSUE.value,
            similarity=0.10,
            customer_message="Random text",
            support_response="Glad to help."
        )
        decision = self.engine.decide(Intent.FARE_OR_CHARGE_ISSUE.value, retrieval)
        self.assertEqual(decision.action, Action.ESCALATE)
        self.assertIn("below threshold", decision.reason)

    def test_escalate_on_support_followup_phrase(self):
        retrieval = RetrievalResult(
            intent=Intent.FARE_OR_CHARGE_ISSUE.value,
            similarity=0.65,
            customer_message="Overcharged for trip",
            support_response="Please send us a DM so we can look into this."
        )
        decision = self.engine.decide(Intent.FARE_OR_CHARGE_ISSUE.value, retrieval)
        self.assertEqual(decision.action, Action.ESCALATE)
        self.assertIn("direct support follow-up", decision.reason)

    def test_auto_handle_on_clear_resolution(self):
        retrieval = RetrievalResult(
            intent=Intent.FARE_OR_CHARGE_ISSUE.value,
            similarity=0.55,
            customer_message="Overcharged for trip",
            support_response="Your fare has been automatically adjusted in the receipts tab."
        )
        decision = self.engine.decide(Intent.FARE_OR_CHARGE_ISSUE.value, retrieval)
        self.assertEqual(decision.action, Action.AUTO_HANDLE)
        self.assertIn("sufficiently similar", decision.reason)

    def test_draft_reply_grounding(self):
        retrieval = RetrievalResult(
            intent=Intent.REFUND_REQUEST.value,
            similarity=0.45,
            customer_message="Need refund",
            support_response="Send us a note with your details."
        )
        reply = self.engine.draft_reply(Intent.REFUND_REQUEST.value, retrieval)
        self.assertIn("DM", reply)


if __name__ == "__main__":
    unittest.main()
