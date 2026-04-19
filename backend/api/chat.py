from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from . import shared

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: Optional[List[Message]] = []


class ChatResponse(BaseModel):
    answer: str
    used_notes: bool
    sources: Optional[List[str]] = None


def create_prompt_template(): 
    return ChatPromptTemplate.from_messages([
        ("system", """You are my helpful Second Brain — a personal AI assistant with access to my private notes.

                You are concise, direct, and professional.

                IMPORTANT RULES:
                - If the user says a simple greeting like "hi", "hello", "hey", or "how are you", respond with a short friendly reply like "Hi! How can I help you today?" and STOP there. Do not add extra information or retrieved notes.
                - For all other questions, answer based on the "Recent notes" below if they are clearly relevant.
                - If the notes are irrelevant or empty, do NOT force an answer from them. Just answer normally from your knowledge.
                - Never start your response with a greeting unless the user greeted you first.
                - Be clear, concise, and to the point. Avoid unnecessary pleasantries."""),
                    
                    MessagesPlaceholder(variable_name="history"),
                    
                    ("human", """Recent notes from my Second Brain:
                {context}

                Current question: {question}"""
        )
    ])


def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant notes."


# Lazy retriever to avoid early execution
def get_retriever():
    return shared.vectorstore.as_retriever(search_kwargs={"k": 4})

def getContext():
    return {
        "context": RunnableLambda(lambda x: get_retriever().invoke(x["question"])) | format_docs,
        "question": RunnablePassthrough(),
        "history": lambda x: x.get("history", []),
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        history_messages = []
        for msg in request.history[-10:]:
            if msg.role.lower() == "user":
                history_messages.append(HumanMessage(content=msg.content))
            elif msg.role.lower() == "assistant":
                history_messages.append(AIMessage(content=msg.content))
        
        chain = (
            getContext()
            | create_prompt_template()
            | shared.llm
            | StrOutputParser()
        )

        answer = await chain.ainvoke({
            "question": question,
            "history": history_messages
        })

        docs = shared.vectorstore.similarity_search(question, k=4)
        sources = [d.metadata.get("source", "unknown") for d in docs] if docs else None

        return ChatResponse(
            answer=answer,
            used_notes=len(docs) > 0,
            sources=sources
        )

    except Exception as e:
        print(f"Chat error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))