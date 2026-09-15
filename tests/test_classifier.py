import unittest
from app.classifier import IntentClassifier
from app.models import Intent


class TestIntentClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = IntentClassifier()

    def test_uber_eats_issue(self):
        msg = "My Uber Eats order never arrived from the restaurant"
        self.assertEqual(self.classifier.classify(msg), Intent.UBER_EATS_ISSUE.value)

    def test_account_access_issue(self):
        msg = "I cannot log in to my account, it says deactivated"
        self.assertEqual(self.classifier.classify(msg), Intent.ACCOUNT_ACCESS_ISSUE.value)

    def test_driver_issue(self):
        msg = "The driver was speeding and rude during pickup"
        self.assertEqual(self.classifier.classify(msg), Intent.DRIVER_ISSUE.value)

    def test_cancellation_issue(self):
        msg = "Why was I charged a cancellation fee after the trip was canceled?"
        # Contains cancel keywords
        intent = self.classifier.classify(msg)
        self.assertIn(intent, [Intent.CANCELLATION_ISSUE.value, Intent.FARE_OR_CHARGE_ISSUE.value])

    def test_refund_request(self):
        msg = "I want a refund and my money back"
        self.assertEqual(self.classifier.classify(msg), Intent.REFUND_REQUEST.value)

    def test_fare_or_charge_issue(self):
        msg = "The price was way too high and I was overcharged with surge"
        self.assertEqual(self.classifier.classify(msg), Intent.FARE_OR_CHARGE_ISSUE.value)

    def test_payment_issue(self):
        msg = "My credit card transaction failed during payment billing"
        self.assertEqual(self.classifier.classify(msg), Intent.PAYMENT_ISSUE.value)

    def test_app_or_technical_issue(self):
        msg = "The app crashed with an error and is not working"
        self.assertEqual(self.classifier.classify(msg), Intent.APP_OR_TECHNICAL_ISSUE.value)

    def test_trip_issue(self):
        msg = "The route was completely wrong before my dropoff"
        self.assertEqual(self.classifier.classify(msg), Intent.TRIP_ISSUE.value)

    def test_other_support_issue_fallback(self):
        msg = "Hello there good morning"
        self.assertEqual(self.classifier.classify(msg), Intent.OTHER_SUPPORT_ISSUE.value)

    def test_get_scores(self):
        msg = "refund my money back please"
        scores = self.classifier.get_scores(msg)
        self.assertGreater(scores[Intent.REFUND_REQUEST.value], 0)


if __name__ == "__main__":
    unittest.main()
