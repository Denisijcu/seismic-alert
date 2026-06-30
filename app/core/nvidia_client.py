
from openai import OpenAI
from app.core.config import settings

client = OpenAI(
    api_key=settings.nvidia_api_key,
    base_url=settings.nvidia_base_url,
)