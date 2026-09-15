from fastapi import APIRouter, HTTPException, status
from app.models import AnalyzeRequest, AnalyzeResponse

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze customer message",
    description="Analyzes customer message through the support agent pipeline. Returns placeholder structure in Step 2."
)
async def analyze_message(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze an incoming customer support message.

    Validates message content and returns the pipeline response contract.
    At this stage, values are returned as clear placeholders without connecting to AI models.
    """
    try:
        return AnalyzeResponse(
            message=request.message,
            intent=None,
            confidence=None,
            historical_match=None,
            similarity=None,
            draft_reply=None,
            decision=None,
            decision_reason=None
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the analysis request: {str(exc)}"
        )
