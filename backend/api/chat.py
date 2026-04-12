from fastapi import APIRouter
import textwrap

from . import shared

router = APIRouter()


@router.post("/chat")
async def chat(request: dict):
    try:
        user_question = request.get("question", "")
        if not user_question:
            return {"error": "Question is required"}

        # Retrieve relevant notes from Chroma
        docs = shared.vectorstore.similarity_search(user_question, k=2)
        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = textwrap.dedent(f"""
        You are my helpful Second Brain. You have access to my personal notes.

        My notes:
        {context}

        User question: {user_question}

        Answer based on my notes if possible. If the notes don't have enough information, say so honestly.
        Be clear, concise, and helpful. Use bullet points when appropriate.
        """)

        response = shared.llm.invoke(prompt)
        return {"answer": response.content}

    except Exception as e:
        return {"error": str(e)}
