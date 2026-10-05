import json
import httpx
from app.core.config import settings
from app.schemas.task import TaskCreate


class AiResponseError(Exception):
    pass


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
        if not isinstance(response_data, dict):
            raise AiResponseError("AI response must be a JSON object")

        response = response_data.get("response")
        if not isinstance(response, str) or not response.strip():
            raise AiResponseError("AI response does not contain generated task JSON")

        try:
            tasks = json.loads(response)
        except json.JSONDecodeError as exc:
            raise AiResponseError("AI response contains invalid task JSON") from exc

        if not isinstance(tasks, dict):
            raise AiResponseError("AI task JSON must be an object")
        task_items = tasks.get("tasks")
        if not isinstance(task_items, list) or not task_items:
            raise AiResponseError("AI task JSON must contain a non-empty tasks list")

        for task in task_items:
            if (
                not isinstance(task, dict)
                or not isinstance(task.get("title"), str)
                or not task["title"].strip()
                or not isinstance(task.get("description"), str)
            ):
                raise AiResponseError("AI task entries must contain a title and description")

        return tasks
    
    def tasks_to_model(self, tasks: dict):
        if not isinstance(tasks, dict):
            raise AiResponseError("AI task data must be an object")
        task_items = tasks.get("tasks")
        if not isinstance(task_items, list) or not task_items:
            raise AiResponseError("AI task data must contain a non-empty tasks list")

        try:
            return [
                TaskCreate(name=task["title"], description=task["description"])
                for task in task_items
            ]
        except (KeyError, TypeError, ValueError) as exc:
            raise AiResponseError("AI task entries have an invalid structure") from exc

    async def generate(self, context):
        payload = self.payload.copy()
        payload["prompt"] = self.base_context + '\n' + context
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError) as exc:
                raise AiResponseError("AI service returned invalid JSON") from exc
            return self.tasks_to_model(self.extract_tasks(response_data))
        