# graph_monthly_multi_agent.py

from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from typing import TypedDict
from datetime import datetime, timedelta
import re

# -----------------------------
# LLM + Vector Store
# -----------------------------
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.3
)

embeddings = OllamaEmbeddings(model="all-minilm")

vectorstore = Chroma(
    collection_name="second_brain_v1",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# -----------------------------
# STATE
# -----------------------------
class GraphState(TypedDict):
    context: str
    draft: str

    structure_feedback: str
    clarity_feedback: str
    depth_feedback: str

    score: int
    previous_score: int
    decision: str
    iteration: int

    final_report: str


# -----------------------------
# 1. RETRIEVE
# -----------------------------
def retrieve(state: GraphState):
    thirty_days_ago = (
        datetime.now() - timedelta(days=30)
    ).strftime("%Y-%m-%d")

    docs = vectorstore.similarity_search(
        f"monthly notes since {thirty_days_ago}",
        k=20
    )

    return {
        "context": "\n\n".join(
            [d.page_content for d in docs]
        ),
        "iteration": 0,
        "previous_score": 0
    }


# -----------------------------
# 2. WRITER
# -----------------------------
def writer(state: GraphState):
    iteration = state.get("iteration", 0)
    import textwrap

    prompt = textwrap.dedent(f"""
        Write a Monthly Deep Analysis Report.

        Context:
        {state['context']}

        Structure:
        - Patterns
        - Achievements
        - Risks
        - Behavioral Trends
        - Next Month Plan

        Rules:
        - Avoid generic statements
        - Be specific and actionable

        Iteration: {iteration}
    """)

    res = llm.invoke(prompt)

    return {"draft": res.content, "iteration": iteration + 1}


# -----------------------------
# 3. PARALLEL CRITICS
# -----------------------------
def structure_agent(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Evaluate structure quality.

        Check:
        - Are all sections present?
        - Are sections meaningful?

        Report issues clearly.

        Text:
        {state['draft']}
    """)
    res = llm.invoke(prompt)

    return {
        "structure_feedback": res.content
    }


def clarity_agent(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Evaluate clarity.

        Identify:
        - vague statements
        - unclear sentences

        Text:
        {state['draft']}
    """)
    res = llm.invoke(prompt)

    return {
        "clarity_feedback": res.content
    }


def depth_agent(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Evaluate depth.

        Decide:
        - shallow OR insightful

        Explain why.

        Text:
        {state['draft']}
    """)
    res = llm.invoke(prompt)

    return {
        "depth_feedback": res.content
    }


# -----------------------------
# 4. SELECTOR
# -----------------------------
def selector(state: GraphState):
    prompt = f"""
        You are a strict evaluator.

        Iteration: {state['iteration']}

        If iteration > 1:
        - be more lenient and finalize if acceptable

        Structure Feedback:
        {state['structure_feedback']}

        Clarity Feedback:
        {state['clarity_feedback']}

        Depth Feedback:
        {state['depth_feedback']}

        Return strictly:
        Score: X/10
        Decision: finalize or rewrite
    """

    import textwrap

    prompt = textwrap.dedent(f"""
        You are a strict evaluator.

        Iteration: {state['iteration']}

        If iteration > 1:
        - be more lenient and finalize if acceptable

        Structure Feedback:
        {state['structure_feedback']}

        Clarity Feedback:
        {state['clarity_feedback']}

        Depth Feedback:
        {state['depth_feedback']}

        Return strictly:
        Score: X/10
        Decision: finalize or rewrite
    """)

    res = llm.invoke(prompt).content

    match = re.search(r"(\d+)/10", res)
    score = int(match.group(1)) if match else 5

    prev_score = state.get("previous_score", 0)

    # no improvement → stop
    if score <= prev_score:
        decision = "finalize"
    else:
        decision = "finalize" if score >= 8 else "rewrite"

    return {
        "score": score,
        "previous_score": score,
        "decision": decision
    }


# -----------------------------
# 5. ROUTER
# -----------------------------
def route(state: GraphState):
    iteration = state.get("iteration", 0)

    # HARD STOP
    if iteration >= 2:
        return "finalize"

    return state.get("decision", "rewrite")


# -----------------------------
# 6. REWRITE
# -----------------------------
def rewrite(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Rewrite the report aggressively.

        Fix ALL issues mentioned.

        Rules:
        - Do NOT repeat wording
        - Improve clarity and depth
        - Make it actionable

        Draft:
        {state['draft']}

        Feedback:
        {state['structure_feedback']}
        {state['clarity_feedback']}
        {state['depth_feedback']}
    """)

    res = llm.invoke(prompt)

    return {"draft": res.content}


# -----------------------------
# 7. FINALIZE
# -----------------------------
def finalize(state: GraphState):
    import textwrap

    prompt = textwrap.dedent(f"""
        Produce final polished Monthly Report.

        Make it:
        - clean
        - structured
        - concise

        Text:
        {state['draft']}
    """)

    res = llm.invoke(prompt)

    return {"final_report": res.content}


# -----------------------------
# BUILD GRAPH
# -----------------------------
def build_graph():
    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("writer", writer)

    workflow.add_node("structure", structure_agent)
    workflow.add_node("clarity", clarity_agent)
    workflow.add_node("depth", depth_agent)

    workflow.add_node("selector", selector)
    workflow.add_node("rewrite", rewrite)
    workflow.add_node("finalize", finalize)

    # Entry
    workflow.set_entry_point("retrieve")

    # Flow
    workflow.add_edge("retrieve", "writer")

    # Parallel critics
    workflow.add_edge("writer", "structure")
    workflow.add_edge("writer", "clarity")
    workflow.add_edge("writer", "depth")

    # Merge
    workflow.add_edge("structure", "selector")
    workflow.add_edge("clarity", "selector")
    workflow.add_edge("depth", "selector")

    # Conditional routing
    workflow.add_conditional_edges(
        "selector",
        route,
        {
            "rewrite": "rewrite",
            "finalize": "finalize"
        }
    )

    # Loop
    workflow.add_edge("rewrite", "writer")

    # End
    workflow.add_edge("finalize", END)

    return workflow.compile()


# -----------------------------
# INSTANCE
# -----------------------------
monthly_graph = build_graph()