from fastapi import APIRouter

from . import shared
import importlib


def _resolve_graph_module(name: str):
    """Try several import paths so the module works whether the app
    is started from the project root (module path `backend.api`) or
    from the `backend` folder (module path `api`)."""
    candidates = [f"..utils.{name}", f"backend.utils.{name}", f"utils.{name}"]
    for cand in candidates:
        try:
            # try relative import (works when package context exists)
            return importlib.import_module(cand, package=__package__)
        except Exception:
            try:
                # try absolute import
                return importlib.import_module(cand)
            except Exception:
                continue
    return None


graph_daily = _resolve_graph_module("graph_daily")
graph_weekly = _resolve_graph_module("graph_weekly")
graph_monthly = _resolve_graph_module("graph_monthly")

router = APIRouter()


@router.post("/daily-summary")
async def daily_summary():
    try:
        if graph_daily:
            result = await graph_daily.generate_daily_summary()
            return {"report": result}
        return {"error": "daily graph module not found"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/weekly-summary")
async def weekly_summary():
    try:
        if graph_weekly:
            result = graph_weekly.weekly_graph.invoke({})
            return {"report": result["final_report"]}

        for cand in ("backend.utils.graph_weekly", "utils.graph_weekly", "graph_weekly"):
            try:
                mod = importlib.import_module(cand)
                result = mod.weekly_graph.invoke({})
                return {"report": result["final_report"]}
            except Exception:
                continue

        return {"error": "weekly graph module not found"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/monthly-summary")
async def monthly_summary():
    try:
        if graph_monthly:
            result = graph_monthly.monthly_graph.invoke({})
            return {"report": result["final_report"]}

        for cand in ("backend.utils.graph_monthly", "utils.graph_monthly", "graph_monthly"):
            try:
                mod = importlib.import_module(cand)
                result = mod.monthly_graph.invoke({})
                return {"report": result["final_report"]}
            except Exception:
                continue

        return {"error": "monthly graph module not found"}
    except Exception as e:
        return {"error": str(e)}
