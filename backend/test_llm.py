"""
Quick diagnostic test to verify Groq LLM connectivity
"""
import asyncio
from app.llm_factory import get_conversational_llm
from langchain_core.messages import SystemMessage, HumanMessage


async def test_llm():
    """Test if Groq LLM responds"""
    print("Testing Groq LLM connection (Llama 3.1)...")
    print("-" * 50)

    llm = get_conversational_llm()
    messages = [
        SystemMessage(content="You are Shruti, an NBFC loan assistant. Respond in 1 brief sentence."),
        HumanMessage(content="Hello Shruti, I want to explore a personal loan.")
    ]

    try:
        response = await llm.ainvoke(messages)
        print("✅ LLM Response:")
        print(response.content)
        print("-" * 50)
        print("✅ Groq LLM is online and operational!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("-" * 50)
        print("❌ Groq LLM connection failed. Check GROQ_API_KEY in backend/.env.")
        return False


if __name__ == "__main__":
    asyncio.run(test_llm())
