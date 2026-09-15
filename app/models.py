from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any


class Intent(str, Enum):
    FARE_OR_CHARGE_ISSUE = "fare_or_charge_issue"
    REFUND_REQUEST = "refund_request"
    DRIVER_ISSUE = "driver_issue"
    TRIP_ISSUE = "trip_issue"
    CANCELLATION_ISSUE = "cancellation_issue"
    ACCOUNT_ACCESS_ISSUE = "account_access_issue"
    PAYMENT_ISSUE = "payment_issue"
    APP_OR_TECHNICAL_ISSUE = "app_or_technical_issue"
    UBER_EATS_ISSUE = "uber_eats_issue"
    OTHER_SUPPORT_ISSUE = "other_support_issue"


class Action(str, Enum):
    AUTO_HANDLE = "AUTO_HANDLE"
    ESCALATE = "ESCALATE"


@dataclass
class RetrievalResult:
    intent: str
    similarity: float
    customer_message: str
    support_response: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentDecision:
    action: Action
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "reason": self.reason
        }


@dataclass
class AgentOutput:
    customer_message: str
    intent: str
    retrieval: Optional[RetrievalResult]
    draft_reply: str
    action: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer_message": self.customer_message,
            "intent": self.intent,
            "retrieval": self.retrieval.to_dict() if self.retrieval else None,
            "draft_reply": self.draft_reply,
            "action": self.action,
            "reason": self.reason
        }
