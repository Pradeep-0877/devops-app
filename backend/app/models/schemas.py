from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    PYTHON_SCRIPT = "python_script"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    DATABASE_QUERY = "database_query"
    SHELL_COMMAND = "shell_command"
    AI_ASSISTED = "ai_assisted"


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime
    last_login: Optional[datetime] = None
    auth_source: str = "local"  # local or ldap


class UserResponse(UserBase):
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    task_type: TaskType
    script_content: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}
    schedule: Optional[str] = None  # Cron expression
    enabled: bool = True
    timeout: int = 3600  # seconds


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    script_content: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
    enabled: Optional[bool] = None
    timeout: Optional[int] = None


class TaskInDB(TaskBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class TaskResponse(TaskInDB):
    pass


class TaskExecutionBase(BaseModel):
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: Optional[str] = None


class TaskExecutionCreate(BaseModel):
    task_id: str
    parameters: Optional[Dict[str, Any]] = {}


class TaskExecutionInDB(TaskExecutionBase):
    id: str
    triggered_by: str
    created_at: datetime


class TaskExecutionResponse(TaskExecutionInDB):
    task_name: Optional[str] = None


class AIPromptRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = {}


class AIPromptResponse(BaseModel):
    response: str
    task_suggestion: Optional[Dict[str, Any]] = None
    confidence: float = 0.0


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    tasks: List[str] = []  # List of task IDs
    enabled: bool = True


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowInDB(WorkflowBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime


class WorkflowResponse(WorkflowInDB):
    pass
