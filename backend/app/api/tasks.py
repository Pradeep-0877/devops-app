from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_current_active_user
from app.models.schemas import (
    TaskCreate, TaskResponse, TaskUpdate,
    TaskExecutionCreate, TaskExecutionResponse
)
from app.models.repositories import TaskRepository, TaskExecutionRepository
from app.services.automation_engine import automation_engine
from loguru import logger

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new automation task"""
    
    task = await TaskRepository.create_task(task_create, created_by=current_user["user_id"])
    
    logger.info(f"Task created: {task.name} by user {current_user['username']}")
    
    return TaskResponse(**task.model_dump())


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user)
):
    """Get all tasks for current user"""
    
    tasks = await TaskRepository.get_user_tasks(current_user["user_id"], skip=skip, limit=limit)
    
    return [TaskResponse(**task.model_dump()) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific task"""
    
    task = await TaskRepository.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user owns the task
    if task.created_by != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    return TaskResponse(**task.model_dump())


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update a task"""
    
    task = await TaskRepository.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.created_by != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    updated_task = await TaskRepository.update_task(task_id, task_update)
    
    logger.info(f"Task updated: {task_id} by user {current_user['username']}")
    
    return TaskResponse(**updated_task.model_dump())


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete a task"""
    
    task = await TaskRepository.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.created_by != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    await TaskRepository.delete_task(task_id)
    
    logger.info(f"Task deleted: {task_id} by user {current_user['username']}")


@router.post("/{task_id}/execute", response_model=TaskExecutionResponse)
async def execute_task(
    task_id: str,
    execution_create: TaskExecutionCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Execute a task immediately"""
    
    task = await TaskRepository.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.created_by != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to execute this task"
        )
    
    # Create execution record
    execution = await TaskExecutionRepository.create_execution(
        execution_create,
        triggered_by=current_user["user_id"]
    )
    
    # Submit task to automation engine
    automation_engine.execute_task_async(execution.id, task, execution_create.parameters or {})
    
    logger.info(f"Task execution started: {task_id} by user {current_user['username']}")
    
    response = TaskExecutionResponse(**execution.model_dump())
    response.task_name = task.name
    
    return response


@router.get("/{task_id}/executions", response_model=List[TaskExecutionResponse])
async def get_task_executions(
    task_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get execution history for a task"""
    
    task = await TaskRepository.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.created_by != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    executions = await TaskExecutionRepository.get_task_executions(task_id, skip=skip, limit=limit)
    
    responses = []
    for execution in executions:
        response = TaskExecutionResponse(**execution.model_dump())
        response.task_name = task.name
        responses.append(response)
    
    return responses


@router.get("/executions/{execution_id}", response_model=TaskExecutionResponse)
async def get_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific execution"""
    
    execution = await TaskExecutionRepository.get_execution_by_id(execution_id)
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # Get task to check ownership
    task = await TaskRepository.get_task_by_id(execution.task_id)
    
    if not task or task.created_by != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this execution"
        )
    
    response = TaskExecutionResponse(**execution.model_dump())
    response.task_name = task.name
    
    return response
