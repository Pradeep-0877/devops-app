from typing import Dict, Any, Optional
from app.core.config import settings
from app.models.schemas import AIPromptResponse, TaskType
from loguru import logger
import json


class AIService:
    """AI Service for natural language processing and task generation"""
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AI client based on provider"""
        if self.provider == "openai" and settings.OPENAI_API_KEY:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        
        elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
        
        else:
            logger.warning(f"AI provider {self.provider} not configured")
    
    async def process_prompt(self, prompt: str, context: Dict[str, Any] = None) -> AIPromptResponse:
        """Process a natural language prompt"""
        
        if not self.client:
            return AIPromptResponse(
                response="AI service is not configured",
                confidence=0.0
            )
        
        try:
            # Build context-aware prompt
            system_prompt = """You are an automation assistant. Help users create and manage automation tasks.
            Analyze the user's request and provide clear, actionable responses.
            If the request is to create an automation, suggest a task definition."""
            
            if context:
                system_prompt += f"\n\nContext: {json.dumps(context)}"
            
            if self.provider == "openai":
                response = await self._process_openai(prompt, system_prompt)
            elif self.provider == "anthropic":
                response = await self._process_anthropic(prompt, system_prompt)
            else:
                response = "AI provider not supported"
            
            return AIPromptResponse(
                response=response,
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"AI prompt processing error: {str(e)}")
            return AIPromptResponse(
                response=f"Error processing prompt: {str(e)}",
                confidence=0.0
            )
    
    async def _process_openai(self, prompt: str, system_prompt: str) -> str:
        """Process prompt using OpenAI"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def _process_anthropic(self, prompt: str, system_prompt: str) -> str:
        """Process prompt using Anthropic Claude"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    async def generate_task_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate a task definition from natural language"""
        
        if not self.client:
            raise Exception("AI service is not configured")
        
        system_prompt = """You are an automation task generator. Convert natural language requests into task definitions.
        Return a JSON object with the following structure:
        {
            "name": "Task name",
            "description": "Task description",
            "task_type": "python_script|api_call|shell_command|file_operation",
            "script_content": "The script/command to execute",
            "parameters": {"key": "value"},
            "schedule": "cron expression (optional)"
        }
        
        Task types:
        - python_script: For Python code execution
        - api_call: For HTTP API requests
        - shell_command: For shell/terminal commands
        - file_operation: For file system operations
        
        Examples:
        Input: "Send me a daily report at 9 AM"
        Output: {
            "name": "Daily Report",
            "description": "Send daily report at 9 AM",
            "task_type": "python_script",
            "script_content": "# Generate and send report\\nresult = {'status': 'report sent'}",
            "schedule": "0 9 * * *"
        }
        """
        
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Generate a task for: {prompt}"}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                task_def = json.loads(response.choices[0].message.content)
            
            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": f"Generate a task for: {prompt}"}
                    ]
                )
                # Extract JSON from response
                content = response.content[0].text
                # Try to find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    task_def = json.loads(content[start_idx:end_idx])
                else:
                    task_def = json.loads(content)
            
            else:
                raise Exception("AI provider not supported")
            
            logger.info(f"Generated task definition: {task_def['name']}")
            return task_def
            
        except Exception as e:
            logger.error(f"Task generation error: {str(e)}")
            raise
    
    async def optimize_script(self, script_content: str, language: str = "python") -> Dict[str, Any]:
        """Optimize a script using AI"""
        
        if not self.client:
            raise Exception("AI service is not configured")
        
        system_prompt = f"""You are a code optimization expert. Analyze the provided {language} script and suggest improvements.
        Return a JSON object with:
        {{
            "script": "Optimized script",
            "improvements": ["List of improvements made"],
            "explanation": "Brief explanation of optimizations"
        }}
        
        Focus on:
        - Performance improvements
        - Code clarity and readability
        - Best practices
        - Error handling
        - Security considerations
        """
        
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Optimize this script:\n\n{script_content}"}
                    ],
                    temperature=0.5,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            
            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": f"Optimize this script:\n\n{script_content}"}
                    ]
                )
                content = response.content[0].text
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    result = json.loads(content[start_idx:end_idx])
                else:
                    result = json.loads(content)
            
            else:
                raise Exception("AI provider not supported")
            
            return result
            
        except Exception as e:
            logger.error(f"Script optimization error: {str(e)}")
            raise


# Global instance
ai_service = AIService()
