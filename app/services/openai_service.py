from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIService:
    @staticmethod
    async def generate_comment_reply(comment_text: str, page_name: str) -> str:
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are an AI assistant managing comments for the Facebook Page '{page_name}'. "
                            "Provide a polite, engaging, concise, and helpful response."
                        )
                    },
                    {"role": "user", "content": f"Comment: {comment_text}"}
                ],
                max_tokens=150,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Thank you for your comment!"

    @staticmethod
    async def answer_support_query(query: str) -> str:
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the official AI Support Agent for 'Facebook Auto Post SaaS'. "
                            "You answer questions regarding setting up Facebook accounts, scheduling posts, "
                            "and managing automated replies. If you are uncertain or the request demands human intervention, "
                            "explicitly include the exact phrase 'CANNOT_ANSWER' in your output."
                        )
                    },
                    {"role": "user", "content": query}
                ],
                max_tokens=250,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "CANNOT_ANSWER"
