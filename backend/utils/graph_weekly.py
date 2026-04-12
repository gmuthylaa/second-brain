from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from typing import TypedDict
from datetime import datetime, timedelta

# Configure LLM and vectorstore similarly to other graph modules
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
    """Retrieve recent notes for weekly summary (last 30 days)"""
    today = datetime.now()
    thirty_days_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")

    query = f"weekly patterns trends tasks projects emotions health work life since {thirty_days_ago} until {today_str}"

    docs = vectorstore.similarity_search(query, k=20)
    context = "\n\n".join([doc.page_content for doc in docs])
    return {"context": context}


def generate_draft(state: GraphState):
    """Generate initial weekly summary"""
    import textwrap

    prompt = textwrap.dedent(f"""
        This is a weekly summary request. The date today is {datetime.now().strftime('%A, %d %B %Y')}.

        Here are recent notes for the past 30 days:
        {state['context']}

        Produce a concise, actionable weekly summary with these sections:

        **Highlights**
        - Major wins, completed tasks, milestones

        **Trends & Patterns**
        - Recurring themes, risks, or opportunities

        **Action Plan**
        - Suggested priorities and next steps for the coming week

        Keep tone helpful and practical. Use bullet points and short paragraphs.
    """)

    response = llm.invoke(prompt)
    return {"draft": response.content}


def critique(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Review the following weekly draft and suggest improvements for clarity, usefulness, and actionability.

        Draft:
        {state['draft']}

        Provide concise critique focused on:
        - Are the priorities clear?
        - Are suggestions actionable?
        - Anything important missing?
    """)

    response = llm.invoke(prompt)
    return {"critique": response.content}


def finalize(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Using the draft and critique below, produce the final weekly summary.

        Draft:
        {state['draft']}

        Critique:
        {state['critique']}

        Output a clear, actionable weekly summary.
    """)

    response = llm.invoke(prompt)
    return {"final_report": response.content}


def build_weekly_graph():
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


weekly_graph = build_weekly_graph()
# graph_weekly.py

from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from typing import TypedDict
from datetime import datetime, timedelta
import re

# -----------------------------
# LLM + Vector DB
# -----------------------------
llm = ChatOllama(model="llama3.2:3b", temperature=0.3)

embeddings = OllamaEmbeddings(model="all-minilm")
vectorstore = Chroma(
    collection_name="second_brain_v1",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# -----------------------------
# Graph State
# -----------------------------
class GraphState(TypedDict):
    context: str
    draft: str
    critique: str
    score: int
    iteration: int
    final_report: str


# -----------------------------
# 1. Retrieve
# -----------------------------
def retrieve_weekly(state: GraphState):
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    import textwrap

    query = textwrap.dedent(f"""
        Weekly review from last 7 days:
        - work progress
        - tasks completed
        - blockers
        - habits
        - health
        - spending
        since {seven_days_ago}
    """)

    docs = vectorstore.similarity_search(query, k=12)
    context = "\n\n".join([doc.page_content for doc in docs])

    return {
        "context": context,
        "iteration": 0
    }


# -----------------------------
# 2. Generate Draft
# -----------------------------
def generate_draft(state: GraphState):
    iteration = state.get("iteration", 0)

    import textwrap

    prompt = textwrap.dedent(f"""
        Today is {datetime.now().strftime('%A, %d %B %Y')}.

        Here are my recent notes:
        {state['context']}

        Write a **Weekly Deep Analysis**.

        Structure:
        - Key Patterns
        - Insights
        - Risks
        - Recommendations
        - Reflection

        Make it clear, practical, and not generic.

        Iteration: {iteration}
    """)

    response = llm.invoke(prompt)

    return {
        "draft": response.content,
        "iteration": iteration + 1
    }


# -----------------------------
# 3. Critique with SCORE
# -----------------------------
def critique(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Review this weekly draft.

        Give:
        1. Score (0–10)
        2. Short feedback

        Format strictly:
        Score: X/10
        Feedback: ...

        Draft:
        {state['draft']}
    """)

    response = llm.invoke(prompt)
    text = response.content

    # Extract score safely
    match = re.search(r"(\d+)/10", text)
    score = int(match.group(1)) if match else 5

    return {
        "critique": text,
        "score": score
    }


# -----------------------------
# 4. Router (NOT a node)
# -----------------------------
def decide(state: GraphState):
    score = state.get("score", 0)
    iteration = state.get("iteration", 0)

    # prevent infinite loop
    if iteration >= 3:
        return "finalize"

    if score >= 8:
        return "finalize"
    else:
        return "rewrite"


# -----------------------------
# 5. Rewrite
# -----------------------------
def rewrite(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Improve the draft using the critique.

        Draft:
        {state['draft']}

        Critique:
        {state['critique']}

        Make it clearer, sharper, and more actionable.
    """)

    response = llm.invoke(prompt)

    return {
        "draft": response.content
    }


# -----------------------------
# 6. Finalize
# -----------------------------
def finalize(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Produce final polished weekly report.

        Draft:
        {state['draft']}

        Make it concise, structured, and high quality.
    """)

    response = llm.invoke(prompt)

    return {
        "final_report": response.content
    }


# -----------------------------
# BUILD GRAPH
# -----------------------------
def build_weekly_graph():
    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("retrieve", retrieve_weekly)
    workflow.add_node("generate_draft", generate_draft)
    workflow.add_node("critique", critique)
    workflow.add_node("rewrite", rewrite)
    workflow.add_node("finalize", finalize)

    # Entry
    workflow.set_entry_point("retrieve")

    # Flow
    workflow.add_edge("retrieve", "generate_draft")
    workflow.add_edge("generate_draft", "critique")

    # ✅ Conditional routing (correct usage)
    workflow.add_conditional_edges(
        "critique",
        decide,
        {
            "rewrite": "rewrite",
            "finalize": "finalize"
        }
    )

    # Loop
    workflow.add_edge("rewrite", "critique")

    # End
    workflow.add_edge("finalize", END)

    return workflow.compile()


# -----------------------------
# INSTANCE
# -----------------------------
weekly_graph = build_weekly_graph()