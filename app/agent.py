import sys
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path when running app/agent.py directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models import AgentOutput
from app.classifier import IntentClassifier
from app.retriever import ResolutionRetriever
from app.decision import DecisionEngine


class SupportAgent:
    """End-to-end AI Support Agent implementing the 5-stage pipeline:

    1. Customer Message
    2. Intent Classification
    3. Historical Resolution Retrieval
    4. Grounded Draft Reply
    5. Action Decision (AUTO_HANDLE vs ESCALATE) + Reason
    """

    def __init__(
        self,
        classifier: Optional[IntentClassifier] = None,
        retriever: Optional[ResolutionRetriever] = None,
        decision_engine: Optional[DecisionEngine] = None,
        data_path: Optional[Path] = None,
        similarity_threshold: float = 0.20
    ):
        self.classifier = classifier or IntentClassifier()
        self.retriever = retriever or ResolutionRetriever(
            data_path=data_path,
            classifier=self.classifier
        )
        self.decision_engine = decision_engine or DecisionEngine(
            similarity_threshold=similarity_threshold
        )

    def process(self, customer_message: str) -> AgentOutput:
        """Process a customer message through the support agent pipeline."""
        # 1. Intent Classification
        intent = self.classifier.classify(customer_message)

        # 2. Historical Resolution Retrieval
        retrieval_results = self.retriever.retrieve(
            query=customer_message,
            intent=intent,
            top_k=1
        )
        best_retrieval = retrieval_results[0] if retrieval_results else None

        # 3. Grounded Draft Reply
        draft_reply = self.decision_engine.draft_reply(
            intent=intent,
            retrieval=best_retrieval
        )

        # 4. Action Decision & Reason
        decision = self.decision_engine.decide(
            intent=intent,
            retrieval=best_retrieval
        )

        return AgentOutput(
            customer_message=customer_message,
            intent=intent,
            retrieval=best_retrieval,
            draft_reply=draft_reply,
            action=decision.action.value,
            reason=decision.reason
        )

    def print_output(self, output: AgentOutput) -> None:
        """Pretty-print the agent pipeline output."""
        print("\n" + "=" * 70)
        print("HIVER AI SUPPORT AGENT - EXECUTION RESULT")
        print("=" * 70)
        print(f"\n[Customer Message]:\n{output.customer_message}")
        print(f"\n[Predicted Intent]:\n{output.intent}")

        if output.retrieval:
            print(f"\n[Historical Match Similarity]: {output.retrieval.similarity:.4f}")
            print(f"[Historical Customer Query]:\n{output.retrieval.customer_message}")
            print(f"[Historical Support Reply]:\n{output.retrieval.support_response}")
        else:
            print("\n[Historical Match]: None found")

        print(f"\n[Draft Reply]:\n{output.draft_reply}")
        print(f"\n[Action Decision]:\n{output.action}")
        print(f"\n[Reason]:\n{output.reason}")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    agent = SupportAgent()

    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = input("Enter customer message (or press enter for demo): ").strip()
        if not message:
            message = "I was charged too much for my Uber ride and want a refund"

    result = agent.process(message)
    agent.print_output(result)
