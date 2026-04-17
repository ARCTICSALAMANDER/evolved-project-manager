from flask import json
import httpx
from app.core.config import settings
from app.schemas.task import TaskCreate


class AiClient:
    def __init__(self, base_url=settings.AI_URL): 
        self.base_url = base_url
        self.payload = {
            "model": "qwen3:4b",
            "format": "json",
            "stream": False, 
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 40,
                "seed": 50,
                "num_predict": 1000,
                "num_ctx": 4096
            }
        }
        self.base_context = """Ты - помощник, который преобразует идеи проектов в JSON-задачи.
                            Твоя задача - разбить задачу на мелкие таски.
                            Твой ответ должен быть СТРОГО В ФОРМАТЕ JSON.
                            Не пиши никаких пояснений, вступлений или заключений. Только чистый JSON.

                            Схема JSON:
                            {
                            "tasks": [
                                {"title": "название задачи", "description": "краткое описание"}
                            ]
                            }

                            Текст для обработки:"""
        
    def extract_tasks(self, response_data: dict):
        thinking = response_data.get("thinking", "{}")
        if isinstance(thinking, str):
            return json.loads(thinking)
        
        return thinking
    
    def tasks_to_model(self, tasks: dict):
        clean_tasks = list()

        for task in tasks.get("tasks", []):
            if not ("title" in task.keys() and "description" in task.keys()):
                continue

            clean_tasks.append(TaskCreate(name=task["title"], description=task["description"]))
        
        return clean_tasks

    async def generate(self, context):
        payload = self.payload.copy()
        payload["prompt"] = self.base_context + '\n' + context
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return self.tasks_to_model(self.extract_tasks(response.json()))
        