from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from datetime import datetime, timedelta
from typing import Dict, Any

from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Reuse your existing models (or import from shared)
llm = ChatOllama(model="llama3.2:3b", temperature=0.3)

embeddings = OllamaEmbeddings(model="all-minilm")
vectorstore = Chroma(
    collection_name="second_brain_v1",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)


# ====================== Prompts ======================

draft_prompt = ChatPromptTemplate.from_template(
    """Today is {today_str}.

        Here are my recent notes from the last 7 days:

        {context}

        Write a natural, well-structured daily summary using this exact format:

        **What Happened Today**
        - Key events, tasks, or activities

        **Patterns & Observations**
        - Any recurring themes or insights

        **Suggestions & Recommendations**
        - Practical suggestions for tomorrow or next steps

        Tone: warm, balanced, and helpful. Use bullet points where appropriate.
        Keep it concise but meaningful.
        Focus on: plans, tasks, activities, expenses, mood, work, health, and daily life.
    """
)

critique_prompt = ChatPromptTemplate.from_template(
    """Review this daily summary draft and give constructive feedback.

        Draft:
        {draft}

        Provide feedback on:
        - Clarity and structure
        - Usefulness of suggestions  
        - Balance (not too negative or overly optimistic)
        - Anything important that might be missing

        Be honest but kind. Output only the critique.
    """
)

finalize_prompt = ChatPromptTemplate.from_template(
        """Improve the draft based on the critique.

        Original Draft:
        {draft}

        Critique:
        {critique}

        Produce the final, clean, polished daily summary.
        Keep the same structure but make it better based on the feedback.
        """
)


# ====================== Helper Functions ======================

def get_date_context() -> Dict[str, str]:
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    
    return {
        "today": today.strftime("%A, %d %B %Y"),
        "today_str": today.strftime("%Y-%m-%d"),
        "seven_days_ago": seven_days_ago.strftime("%Y-%m-%d")
    }


def retrieve_notes(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve relevant notes for the last 7 days"""
    dates = get_date_context()
    
    # Smart query combining keywords + date context
    query = f"plans tasks activities expenses mood work health daily life today {dates['today_str']} since {dates['seven_days_ago']}"

    docs = vectorstore.similarity_search(query, k=10)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    return {"context": context, **dates}


# ====================== Build the Chain ======================

daily_summary_chain = (
    RunnablePassthrough()               # Start with empty input
    | retrieve_notes                    # Step 1: Retrieve
    | RunnablePassthrough.assign(       # Step 2: Generate Draft
        draft = draft_prompt | llm | StrOutputParser()
    )
    | RunnablePassthrough.assign(       # Step 3: Critique
        critique = critique_prompt | llm | StrOutputParser()
    )
    | finalize_prompt                   # Step 4: Finalize
    | llm
    | StrOutputParser()
)


# ====================== Usage ======================

async def generate_daily_summary():
    """Call this to generate today's summary"""
    result = await daily_summary_chain.ainvoke({})
    return result