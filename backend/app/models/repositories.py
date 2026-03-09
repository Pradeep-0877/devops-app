from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.models.database import get_database
from app.models.schemas import (
    UserCreate, UserInDB, UserUpdate,
    TaskCreate, TaskInDB, TaskUpdate,
    TaskExecutionCreate, TaskExecutionInDB, TaskStatus,
    WorkflowCreate, WorkflowInDB
)
from app.core.security import get_password_hash


class UserRepository:
    """User data access layer"""
    
    @staticmethod
    async def create_user(user: UserCreate, auth_source: str = "local") -> UserInDB:
        """Create a new user"""
        db = get_database()
        
        user_dict = user.model_dump()
        hashed_password = get_password_hash(user_dict.pop("password"))
        
        user_data = {
            **user_dict,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "auth_source": auth_source
        }
        
        result = await db.users.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
        
        return UserInDB(**user_data)
    
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[UserInDB]:
        """Get user by username"""
        db = get_database()
        user_data = await db.users.find_one({"username": username})
        
        if user_data:
            user_data["id"] = str(user_data.pop("_id"))
            return UserInDB(**user_data)
        return None
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        db = get_database()
        user_data = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if user_data:
            user_data["id"] = str(user_data.pop("_id"))
            return UserInDB(**user_data)
        return None
    
    @staticmethod
    async def update_user(user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update user"""
        db = get_database()
        
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        result = await db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["id"] = str(result.pop("_id"))
            return UserInDB(**result)
        return None
    
    @staticmethod
    async def update_last_login(user_id: str):
        """Update user's last login timestamp"""
        db = get_database()
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )


class TaskRepository:
    """Task data access layer"""
    
    @staticmethod
    async def create_task(task: TaskCreate, created_by: str) -> TaskInDB:
        """Create a new task"""
        db = get_database()
        
        task_data = {
            **task.model_dump(),
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_run": None,
            "next_run": None
        }
        
        result = await db.tasks.insert_one(task_data)
        task_data["id"] = str(result.inserted_id)
        
        return TaskInDB(**task_data)
    
    @staticmethod
    async def get_task_by_id(task_id: str) -> Optional[TaskInDB]:
        """Get task by ID"""
        db = get_database()
        task_data = await db.tasks.find_one({"_id": ObjectId(task_id)})
        
        if task_data:
            task_data["id"] = str(task_data.pop("_id"))
            return TaskInDB(**task_data)
        return None
    
    @staticmethod
    async def get_user_tasks(user_id: str, skip: int = 0, limit: int = 100) -> List[TaskInDB]:
        """Get tasks created by user"""
        db = get_database()
        cursor = db.tasks.find({"created_by": user_id}).skip(skip).limit(limit)
        
        tasks = []
        async for task_data in cursor:
            task_data["id"] = str(task_data.pop("_id"))
            tasks.append(TaskInDB(**task_data))
        
        return tasks
    
    @staticmethod
    async def update_task(task_id: str, task_update: TaskUpdate) -> Optional[TaskInDB]:
        """Update task"""
        db = get_database()
        
        update_data = task_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.tasks.find_one_and_update(
            {"_id": ObjectId(task_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["id"] = str(result.pop("_id"))
            return TaskInDB(**result)
        return None
    
    @staticmethod
    async def delete_task(task_id: str) -> bool:
        """Delete task"""
        db = get_database()
        result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0


class TaskExecutionRepository:
    """Task execution data access layer"""
    
    @staticmethod
    async def create_execution(execution: TaskExecutionCreate, triggered_by: str) -> TaskExecutionInDB:
        """Create a new task execution"""
        db = get_database()
        
        execution_data = {
            **execution.model_dump(),
            "triggered_by": triggered_by,
            "status": TaskStatus.PENDING,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "logs": ""
        }
        
        result = await db.task_executions.insert_one(execution_data)
        execution_data["id"] = str(result.inserted_id)
        
        return TaskExecutionInDB(**execution_data)
    
    @staticmethod
    async def get_execution_by_id(execution_id: str) -> Optional[TaskExecutionInDB]:
        """Get execution by ID"""
        db = get_database()
        execution_data = await db.task_executions.find_one({"_id": ObjectId(execution_id)})
        
        if execution_data:
            execution_data["id"] = str(execution_data.pop("_id"))
            return TaskExecutionInDB(**execution_data)
        return None
    
    @staticmethod
    async def get_task_executions(task_id: str, skip: int = 0, limit: int = 50) -> List[TaskExecutionInDB]:
        """Get executions for a task"""
        db = get_database()
        cursor = db.task_executions.find({"task_id": task_id}).sort("created_at", -1).skip(skip).limit(limit)
        
        executions = []
        async for execution_data in cursor:
            execution_data["id"] = str(execution_data.pop("_id"))
            executions.append(TaskExecutionInDB(**execution_data))
        
        return executions
    
    @staticmethod
    async def update_execution_status(
        execution_id: str,
        status: TaskStatus,
        result: dict = None,
        error: str = None,
        logs: str = None
    ) -> Optional[TaskExecutionInDB]:
        """Update execution status"""
        db = get_database()
        
        update_data = {"status": status}
        
        if status == TaskStatus.RUNNING:
            update_data["started_at"] = datetime.utcnow()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            update_data["completed_at"] = datetime.utcnow()
        
        if result is not None:
            update_data["result"] = result
        if error is not None:
            update_data["error"] = error
        if logs is not None:
            update_data["logs"] = logs
        
        result = await db.task_executions.find_one_and_update(
            {"_id": ObjectId(execution_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["id"] = str(result.pop("_id"))
            return TaskExecutionInDB(**result)
        return None
