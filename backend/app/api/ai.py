from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_active_user
from app.models.schemas import AIPromptRequest, AIPromptResponse
from app.services.ai_service import ai_service
from loguru import logger

router = APIRouter()


@router.post("/prompt", response_model=AIPromptResponse)
async def process_ai_prompt(
    request: AIPromptRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Process an AI prompt and get suggestions"""
    
    try:
        response = await ai_service.process_prompt(request.prompt, request.context)
        
        logger.info(f"AI prompt processed for user {current_user['username']}")
        
        return response
        
    except Exception as e:
        logger.error(f"AI prompt processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process AI prompt: {str(e)}"
        )


@router.post("/generate-task", response_model=dict)
async def generate_task_from_prompt(
    request: AIPromptRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Generate a task definition from natural language"""
    
    try:
        task_definition = await ai_service.generate_task_from_prompt(request.prompt)
        
        logger.info(f"Task generated from AI for user {current_user['username']}")
        
        return task_definition
        
    except Exception as e:
        logger.error(f"Task generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate task: {str(e)}"
        )


@router.post("/optimize-script", response_model=dict)
async def optimize_script(
    request: dict,
    current_user: dict = Depends(get_current_active_user)
):
    """Optimize a script using AI"""
    
    script_content = request.get("script_content")
    language = request.get("language", "python")
    
    if not script_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="script_content is required"
        )
    
    try:
        optimized = await ai_service.optimize_script(script_content, language)
        
        logger.info(f"Script optimized for user {current_user['username']}")
        
        return {
            "original": script_content,
            "optimized": optimized["script"],
            "improvements": optimized["improvements"]
        }
        
    except Exception as e:
        logger.error(f"Script optimization error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize script: {str(e)}"
        )
