import asyncio
import subprocess
import json
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.schemas import TaskInDB, TaskType, TaskStatus
from app.models.repositories import TaskExecutionRepository
from loguru import logger
from celery import Celery
from app.core.config import settings

# Initialize Celery
celery_app = Celery(
    "automation_engine",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


class AutomationEngine:
    """Core automation execution engine"""
    
    def __init__(self):
        self.running_tasks = {}
    
    def execute_task_async(self, execution_id: str, task: TaskInDB, parameters: Dict[str, Any]):
        """Submit task for async execution"""
        execute_task_celery.delay(execution_id, task.model_dump(), parameters)
    
    async def execute_task_sync(self, execution_id: str, task: TaskInDB, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task synchronously (for testing or immediate results)"""
        return await self._execute_task(execution_id, task, parameters)
    
    async def _execute_task(self, execution_id: str, task: TaskInDB, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Internal task execution logic"""
        
        logger.info(f"Starting execution {execution_id} for task {task.name}")
        
        # Update status to running
        await TaskExecutionRepository.update_execution_status(
            execution_id,
            TaskStatus.RUNNING
        )
        
        try:
            result = None
            logs = []
            
            if task.task_type == TaskType.PYTHON_SCRIPT:
                result, logs = await self._execute_python_script(task, parameters)
            
            elif task.task_type == TaskType.SHELL_COMMAND:
                result, logs = await self._execute_shell_command(task, parameters)
            
            elif task.task_type == TaskType.API_CALL:
                result, logs = await self._execute_api_call(task, parameters)
            
            elif task.task_type == TaskType.FILE_OPERATION:
                result, logs = await self._execute_file_operation(task, parameters)
            
            else:
                raise ValueError(f"Unsupported task type: {task.task_type}")
            
            # Update status to completed
            await TaskExecutionRepository.update_execution_status(
                execution_id,
                TaskStatus.COMPLETED,
                result=result,
                logs="\n".join(logs)
            )
            
            logger.info(f"Execution {execution_id} completed successfully")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Execution {execution_id} failed: {error_msg}")
            
            await TaskExecutionRepository.update_execution_status(
                execution_id,
                TaskStatus.FAILED,
                error=error_msg
            )
            
            raise
    
    async def _execute_python_script(self, task: TaskInDB, parameters: Dict[str, Any]) -> tuple:
        """Execute a Python script"""
        logs = []
        
        try:
            # Prepare script with parameters
            script = task.script_content
            
            # Create a restricted execution environment
            safe_builtins = {
                k: v for k, v in __builtins__.__dict__.items()
                if k not in ('exec', 'eval', 'compile', '__import__', 'open',
                             'getattr', 'setattr', 'delattr', 'globals', 'locals',
                             'breakpoint', 'exit', 'quit')
            } if isinstance(__builtins__, type(__builtins__)) else {
                k: v for k, v in __builtins__.items()
                if k not in ('exec', 'eval', 'compile', '__import__', 'open',
                             'getattr', 'setattr', 'delattr', 'globals', 'locals',
                             'breakpoint', 'exit', 'quit')
            }
            exec_globals = {
                'parameters': parameters,
                'print': lambda *args: logs.append(' '.join(map(str, args))),
                '__builtins__': safe_builtins
            }
            
            # Execute script
            exec(script, exec_globals)
            
            # Get result if script sets it
            result = exec_globals.get('result', {'status': 'success'})
            
            return result, logs
            
        except Exception as e:
            logs.append(f"Error: {str(e)}")
            raise
    
    async def _execute_shell_command(self, task: TaskInDB, parameters: Dict[str, Any]) -> tuple:
        """Execute a shell command"""
        logs = []
        
        try:
            command = task.script_content
            
            # Replace parameters in command using allowlist validation
            import re
            for key, value in parameters.items():
                sanitized_value = re.sub(r'[;&|`$(){}\[\]!]', '', str(value))
                command = command.replace(f"${{{key}}}", sanitized_value)
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            logs.append(stdout.decode() if stdout else "")
            if stderr:
                logs.append(f"STDERR: {stderr.decode()}")
            
            result = {
                'exit_code': process.returncode,
                'stdout': stdout.decode() if stdout else "",
                'stderr': stderr.decode() if stderr else ""
            }
            
            if process.returncode != 0:
                raise Exception(f"Command failed with exit code {process.returncode}")
            
            return result, logs
            
        except Exception as e:
            logs.append(f"Error: {str(e)}")
            raise
    
    async def _execute_api_call(self, task: TaskInDB, parameters: Dict[str, Any]) -> tuple:
        """Execute an API call"""
        import httpx
        
        logs = []
        
        try:
            config = task.parameters or {}
            
            url = config.get('url')
            method = config.get('method', 'GET').upper()
            headers = config.get('headers', {})
            body = config.get('body', {})
            
            # Replace parameters
            for key, value in parameters.items():
                if isinstance(body, dict):
                    body = json.loads(json.dumps(body).replace(f"${{{key}}}", str(value)))
            
            logs.append(f"Making {method} request to {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if method in ['POST', 'PUT', 'PATCH'] else None,
                    timeout=task.timeout
                )
            
            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
            
            logs.append(f"Response status: {response.status_code}")
            
            return result, logs
            
        except Exception as e:
            logs.append(f"Error: {str(e)}")
            raise
    
    async def _execute_file_operation(self, task: TaskInDB, parameters: Dict[str, Any]) -> tuple:
        """Execute a file operation"""
        import os
        import shutil
        
        logs = []
        
        try:
            config = task.parameters or {}
            operation = config.get('operation')  # read, write, copy, move, delete

            # Validate paths to prevent path traversal
            ALLOWED_BASE = os.environ.get('FILE_OPS_BASE_DIR', '/app/data')
            def _validate_path(p: str) -> str:
                resolved = os.path.realpath(p)
                if not resolved.startswith(os.path.realpath(ALLOWED_BASE)):
                    raise ValueError(f"Path '{p}' is outside the allowed directory")
                return resolved

            if operation == 'read':
                file_path = _validate_path(parameters.get('file_path'))
                with open(file_path, 'r') as f:
                    content = f.read()
                result = {'content': content, 'size': len(content)}
                logs.append(f"Read {len(content)} bytes from {file_path}")
            
            elif operation == 'write':
                file_path = _validate_path(parameters.get('file_path'))
                content = parameters.get('content')
                with open(file_path, 'w') as f:
                    f.write(content)
                result = {'bytes_written': len(content)}
                logs.append(f"Wrote {len(content)} bytes to {file_path}")
            
            elif operation == 'copy':
                source = _validate_path(parameters.get('source'))
                destination = _validate_path(parameters.get('destination'))
                shutil.copy2(source, destination)
                result = {'source': source, 'destination': destination}
                logs.append(f"Copied {source} to {destination}")
            
            elif operation == 'move':
                source = _validate_path(parameters.get('source'))
                destination = _validate_path(parameters.get('destination'))
                shutil.move(source, destination)
                result = {'source': source, 'destination': destination}
                logs.append(f"Moved {source} to {destination}")
            
            elif operation == 'delete':
                file_path = _validate_path(parameters.get('file_path'))
                os.remove(file_path)
                result = {'deleted': file_path}
                logs.append(f"Deleted {file_path}")
            
            else:
                raise ValueError(f"Unsupported file operation: {operation}")
            
            return result, logs
            
        except Exception as e:
            logs.append(f"Error: {str(e)}")
            raise


# Celery task for async execution
@celery_app.task(name="execute_task")
def execute_task_celery(execution_id: str, task_dict: Dict, parameters: Dict[str, Any]):
    """Celery task wrapper for async execution"""
    from app.models.schemas import TaskInDB
    
    task = TaskInDB(**task_dict)
    engine = AutomationEngine()
    
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(engine._execute_task(execution_id, task, parameters))
        return result
    finally:
        loop.close()


# Global instance
automation_engine = AutomationEngine()
