from fastapi import APIRouter, HTTPException, status
from app.models import AnalyzeRequest, AnalyzeResponse
from app.services.support_agent import analyze_customer_message

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze customer message",
    description="Executes the full 5-stage AI support agent pipeline on the incoming customer message."
)
async def analyze_message(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze an incoming customer support message.

    Executes intent classification, intent-filtered historical resolution retrieval,
    draft reply generation, and routing decision.
    """
    try:
        result = analyze_customer_message(request.message)
        return AnalyzeResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Support agent analysis error: {str(exc)}"
        )
