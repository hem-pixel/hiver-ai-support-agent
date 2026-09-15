import unittest
from app.retriever import ResolutionRetriever
from app.models import RetrievalResult


class TestResolutionRetriever(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.retriever = ResolutionRetriever()

    def test_retrieve_returns_results(self):
        query = "I was overcharged for my ride"
        results = self.retriever.retrieve(query, top_k=2)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], RetrievalResult)
        self.assertGreaterEqual(results[0].similarity, 0.0)
        self.assertTrue(len(results[0].support_response) > 0)

    def test_retrieve_with_explicit_intent(self):
        query = "food was cold and delivered late"
        results = self.retriever.retrieve(query, intent="uber_eats_issue", top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].intent, "uber_eats_issue")

    def test_empty_query(self):
        results = self.retriever.retrieve("")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
