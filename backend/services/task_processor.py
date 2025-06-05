"""
Task processor service for executing tasks with directors
Handles task delegation, execution, and result processing
"""

import asyncio
import logging
import json
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.database.models import Task, Director, BoardSession
from backend.utils.privacy_shield import privacy_shield
from backend.config import settings

logger = logging.getLogger(__name__)


class TaskProcessor:
    """Processes tasks by delegating to appropriate directors"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.session = None
        self.current_chairperson_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a single task"""
        try:
            # Select appropriate director
            director = await self._select_director(task)
            
            if not director:
                return {
                    "success": False,
                    "error": "No available director found"
                }
            
            # Execute task
            result = await self.execute_task(task, director)
            
            # Update director metrics
            await self._update_director_metrics(director, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_task(self, task: Task, director: Director) -> Dict[str, Any]:
        """Execute task with specific director"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Prepare task data
            task_data = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "requirements": task.requirements,
                "deliverables": task.deliverables,
                "priority": task.priority
            }
            
            # Filter PII from task data
            filtered_data, filter_log = privacy_shield.filter_request(
                task_data,
                request_id=str(task.id)
            )
            
            # Prepare request based on director type
            request_data = self._prepare_request(director, filtered_data)
            
            # Make request to director endpoint
            headers = {}
            if director.api_key_encrypted:
                # In production, decrypt the API key
                headers["Authorization"] = f"Bearer {director.api_key_encrypted}"
            
            timeout = aiohttp.ClientTimeout(total=settings.TASK_TIMEOUT)
            
            async with self.session.post(
                director.endpoint,
                json=request_data,
                headers=headers,
                timeout=timeout
            ) as response:
                
                if response.status == 200:
                    result_data = await response.json()
                    
                    # Filter PII from response
                    filtered_result, _ = privacy_shield.filter_response(
                        result_data,
                        request_id=str(task.id)
                    )
                    
                    # Assess quality
                    quality_score = self._assess_quality(filtered_result)
                    
                    return {
                        "success": True,
                        "director": director.name,
                        "result": filtered_result,
                        "quality": quality_score,
                        "filter_log": filter_log
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "director": director.name,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except asyncio.TimeoutError:
            return {
                "success": False,
                "director": director.name,
                "error": "Task execution timeout"
            }
        except Exception as e:
            logger.error(f"Error executing task with {director.name}: {e}")
            return {
                "success": False,
                "director": director.name,
                "error": str(e)
            }
    
    async def _select_director(self, task: Task) -> Optional[Director]:
        """Select the best director for a task"""
        # Get available directors
        result = await self.db.execute(
            select(Director).where(Director.is_available == True)
        )
        directors = result.scalars().all()
        
        if not directors:
            return None
        
        # Extract keywords from task
        task_keywords = self._extract_keywords(task)
        
        # Score each director
        director_scores = []
        for director in directors:
            score = self._score_director(director, task_keywords)
            director_scores.append((director, score))
        
        # Sort by score and select best
        director_scores.sort(key=lambda x: x[1], reverse=True)
        
        return director_scores[0][0] if director_scores else None
    
    def _extract_keywords(self, task: Task) -> List[str]:
        """Extract keywords from task for matching"""
        keywords = []
        
        # From title and description
        if task.title:
            keywords.extend(task.title.lower().split())
        if task.description:
            keywords.extend(task.description.lower().split())
        
        # From requirements
        for req in task.requirements:
            if isinstance(req, str):
                keywords.extend(req.lower().split())
        
        return keywords
    
    def _score_director(self, director: Director, keywords: List[str]) -> float:
        """Score director based on task keywords"""
        score = 0.0
        
        # Match specialties
        for specialty in director.specialties:
            specialty_lower = specialty.lower()
            for keyword in keywords:
                if specialty_lower in keyword or keyword in specialty_lower:
                    score += 2.0
        
        # Consider performance metrics
        score += director.overall_score * 3.0
        
        # Boost for current chairperson
        if self.current_chairperson_id and director.id == self.current_chairperson_id:
            score += 1.0
        
        return score
    
    def _prepare_request(self, director: Director, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on director type"""
        # For Ollama models
        if "ollama" in director.endpoint or "11434" in director.endpoint:
            prompt = self._format_task_prompt(task_data)
            
            # Map director names to model names
            model_mapping = {
                "DeepSeek-Coder": "deepseek-coder:6.7b",
                "Mixtral": "mistral:latest",
                "Llama2": "llama2:latest"
            }
            
            return {
                "model": model_mapping.get(director.name, "mistral:latest"),
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            }
        
        # For OpenAI API
        elif "openai.com" in director.endpoint:
            prompt = self._format_task_prompt(task_data)
            return {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
        
        # For Anthropic API
        elif "anthropic.com" in director.endpoint:
            prompt = self._format_task_prompt(task_data)
            return {
                "model": "claude-3-opus-20240229",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000
            }
        
        # Generic format
        else:
            return {
                "task": task_data,
                "director": director.name
            }
    
    def _format_task_prompt(self, task_data: Dict[str, Any]) -> str:
        """Format task as a prompt"""
        prompt = f"Task: {task_data.get('title', 'Unnamed Task')}\n\n"
        
        if task_data.get('description'):
            prompt += f"Description: {task_data['description']}\n\n"
        
        if task_data.get('requirements'):
            prompt += "Requirements:\n"
            for req in task_data['requirements']:
                prompt += f"- {req}\n"
            prompt += "\n"
        
        if task_data.get('deliverables'):
            prompt += "Deliverables:\n"
            for deliverable in task_data['deliverables']:
                if isinstance(deliverable, dict):
                    prompt += f"- {deliverable.get('description', str(deliverable))}\n"
                else:
                    prompt += f"- {deliverable}\n"
        
        prompt += "\nPlease provide a detailed response addressing all requirements and deliverables."
        
        return prompt
    
    def _assess_quality(self, result: Any) -> float:
        """Assess quality of task result"""
        if not result:
            return 0.0
        
        score = 0.5  # Base score
        
        # Check response structure
        if isinstance(result, dict):
            # Has structured response
            if 'response' in result or 'result' in result:
                score += 0.1
            
            # Has code/implementation
            if any(key in result for key in ['code', 'implementation', 'solution']):
                score += 0.2
            
            # No errors
            if 'error' not in result:
                score += 0.1
            
            # Check response length
            response_text = str(result.get('response', result.get('result', '')))
            if len(response_text) > 200:
                score += 0.1
            if len(response_text) > 500:
                score += 0.1
        
        elif isinstance(result, str):
            # String response
            if len(result) > 200:
                score += 0.2
            if len(result) > 500:
                score += 0.1
        
        return min(1.0, score)
    
    async def _update_director_metrics(self, director: Director, result: Dict[str, Any]):
        """Update director performance metrics"""
        try:
            if result['success']:
                director.tasks_completed += 1
                
                # Add quality score
                quality_scores = director.quality_scores or []
                quality_scores.append(result.get('quality', 0.8))
                
                # Keep only recent scores
                if len(quality_scores) > settings.PERFORMANCE_HISTORY_LIMIT:
                    quality_scores = quality_scores[-settings.PERFORMANCE_HISTORY_LIMIT:]
                
                director.quality_scores = quality_scores
            else:
                director.tasks_failed += 1
            
            # Update execution time (would need to track this properly)
            director.total_execution_time += 1.0  # Placeholder
            
            director.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update director metrics: {e}")
            await self.db.rollback()