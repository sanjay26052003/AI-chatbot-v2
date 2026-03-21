from openai import AsyncOpenAI
from config import get_settings
from typing import List, Dict, Any

settings = get_settings()

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def get_ai_response(messages: List[Dict[str, Any]]) -> str:
    """
    Get AI response from OpenAI GPT model.
    messages: List of message dicts with 'role' and 'content' keys
    """
    if not settings.OPENAI_API_KEY:
        return "AI service is not configured. Please set OPENAI_API_KEY in your .env file."

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"
