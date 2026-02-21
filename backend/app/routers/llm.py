"""LLM-powered text generation endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm_service import LlmFeature, generate, is_available

router = APIRouter(prefix="/llm", tags=["llm"])


class GenerateRequest(BaseModel):
    feature: LlmFeature
    context: dict | None = None


class GenerateResponse(BaseModel):
    text: str
    feature: str
    is_mock: bool


class StatusResponse(BaseModel):
    available: bool
    mock_mode: bool


@router.get("/status", response_model=StatusResponse)
async def llm_status():
    """Check if LLM service is available."""
    avail = await is_available()
    return StatusResponse(available=avail, mock_mode=not avail)


@router.post("/generate", response_model=GenerateResponse)
async def llm_generate(req: GenerateRequest):
    """Generate AI-enhanced text for a given feature."""
    result = await generate(req.feature, req.context)
    return GenerateResponse(
        text=result.text,
        feature=result.feature.value,
        is_mock=result.is_mock,
    )
