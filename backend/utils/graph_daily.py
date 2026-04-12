from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from typing import TypedDict, Annotated
import operator
from datetime import datetime, timedelta

llm = ChatOllama(model="llama3.2:3b", temperature=0.3)

embeddings = OllamaEmbeddings(model="all-minilm")
vectorstore = Chroma(
    collection_name="second_brain_v1",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

class GraphState(TypedDict):
    context: str
    draft: str
    critique: str
    final_report: str

def retrieve(state: GraphState):
    """Retrieve recent notes for daily summary (last 7 days)"""
    from datetime import datetime, timedelta
    
    today = datetime.now()
    seven_days_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    # Smart query that includes date context
    query = f"plans tasks activities expenses mood work health daily life today {today_str} recent since {seven_days_ago}"

    # Simple similarity search with better query (most reliable for now)
    docs = vectorstore.similarity_search(query, k=10)

    context = "\n\n".join([doc.page_content for doc in docs])
    
    return {"context": context}

def generate_draft(state: GraphState):
    """Generate initial summary"""
    import textwrap

    prompt = textwrap.dedent(f"""
        Today is {datetime.now().strftime('%A, %d %B %Y')}.

        Here are my recent notes:
        {state['context']}

        Write a natural, well-structured daily summary.

        Use this format:

        **What Happened Today**
        - Key events, tasks, or activities

        **Patterns & Observations**
        - Any recurring themes or insights

        **Suggestions & Recommendations**
        - Practical suggestions for tomorrow or next steps

        Keep the tone warm, balanced, and helpful. Use bullet points where appropriate.
        """)

    response = llm.invoke(prompt)
    return {"draft": response.content}

def critique(state: GraphState):
    """Critique the draft"""
    import textwrap

    prompt = textwrap.dedent(f"""
        Review this draft daily summary and suggest improvements:

        Draft:
        {state['draft']}

        Provide constructive feedback on:
        - Clarity and structure
        - Usefulness of suggestions
        - Balance (not too negative or overly optimistic)
        - Anything missing

        Be honest but kind.
    """)

    response = llm.invoke(prompt)
    return {"critique": response.content}

def finalize(state: GraphState):
    """Produce final polished report"""
    import textwrap

    prompt = textwrap.dedent(f"""
        Improve the draft based on the critique.

        Draft:
        {state['draft']}

        Critique:
        {state['critique']}

        Produce the final, clean, and helpful daily summary.
        """)

    response = llm.invoke(prompt)
    return {"final_report": response.content}

def build_daily_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate_draft", generate_draft)
    workflow.add_node("critique", critique)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate_draft")
    workflow.add_edge("generate_draft", "critique")
    workflow.add_edge("critique", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()

daily_graph = build_daily_graph()