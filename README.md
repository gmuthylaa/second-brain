# Second Brain

A small personal knowledge-work application: a FastAPI backend that ingests files and text, stores embeddings in a local Chroma vector store, and a React + Vite frontend to interact with it.

This README documents how to set up the project locally, run the backend and frontend, and troubleshoot common issues.

## Tech stack
- Backend: Python 3.11+/FastAPI, Uvicorn
- Vector DB: Chroma (local storage)
- LLM/embeddings: LangChain adapters (configured in the backend)
- Frontend: React + TypeScript, Vite

## LangChain, LangGraph and RAG integration

Where they're used
- LangChain is used in the backend to manage embeddings, vector store retrieval, and to invoke LLMs. See `backend/api/shared.py` for the setup of embeddings, Chroma vector store, and the LLM wrapper.
- LangGraph (StateGraph/workflows) is used for higher-level summary workflows (daily/weekly/monthly) implemented under `backend/utils/graph_*.py` and orchestrated by `backend/api/summaries.py`.

How RAG (Retrieval-Augmented Generation) is implemented
- Ingest: files uploaded via the API endpoints under `backend/api/ingest.py` are text-extracted (OCR where needed), split into chunks, embedded using the configured embeddings adapter, and persisted into the local Chroma vector store (see `backend/api/shared.py` and `backend/utils/ocr_image_to_text.py`).
- Retrieval: the summaries and chat endpoints perform a similarity search against the Chroma vector store to retrieve relevant chunks. Retrieval code lives near the endpoint implementations (for example, `backend/api/search.py` and `backend/api/summaries.py`) and uses the vectorstore API to get top-k candidates.
- Generation: retrieved context chunks are passed into prompt templates and then to the LLM (via LangChain adapter) to generate the final answer or report.

How the React UI integrates with RAG
- Frontend actions (uploading files, requesting summaries, and chatting) call backend endpoints through the centralized helpers in `frontend/src/lib/api.ts`.
- UI flows:
	- Ingest page (`frontend/src/pages/Ingest.tsx`) lets users upload files or quick notes; files are POSTed to `/ingest` and images can be reviewed via `/ingest/review`.
	- Summary pages/buttons call the `/daily-summary`, `/weekly-summary`, and `/monthly-summary` endpoints which trigger the LangGraph workflows on the backend to run retrieval + generation.
	- Chat uses `frontend/src/contexts/AppContext.tsx` which sends user questions to `/chat` (backend retrieves context from Chroma and returns an answer).

Notes and developer pointers
- Prompt templates and LLM orchestration are mostly defined inside the graph workflows (`backend/utils/graph_*.py`) and `backend/api/summaries.py` where prompt strings are prepared and fed to the LLM.
- If you switch LLM providers or change embeddings, update `backend/api/shared.py` to instantiate the correct embeddings and LLM adapters and ensure the embeddings shape is compatible with the vector store.
- For unit testing RAG flows, mock the vectorstore retrieval and the LLM call surfaces so you can test orchestration without networked LLM calls.

## Quick start (high-level)
1. Create and activate a Python virtual environment for the backend (recommended: `python -m venv sb-venv` or use the provided `sb-venv/`).
2. Install backend dependencies: `pip install -r backend/requirements.txt` (also ensure `pydantic-settings` is installed for Pydantic v2 settings support).
3. Start the backend: `uvicorn backend.api.app:app --reload` (run from the repo root).
4. Start the frontend: `cd frontend && npm install && npm run dev` and open the app in your browser.

## Backend — setup and run

1. Create and activate a virtual environment (example using the included venv is fine):

	 ```bash
	 python -m venv sb-venv
	 source sb-venv/bin/activate
	 ```

2. Install the backend dependencies:

	 ```bash
	 pip install -r backend/requirements.txt
	 # If you use Pydantic v2, install pydantic-settings as well:
	 pip install pydantic-settings
	 ```

3. Environment variables

	 - The backend reads configuration via Pydantic settings. Common variables you may need to set (see `backend/api/settings.py` for the authoritative list):
		 - `CORS_ORIGINS` — a comma-separated list of allowed origins (optional). If not set, CORS will not be enabled.
		 - Any host/API keys required by your LLM/embedding adapters (for example, server/host names or provider keys) — configure these per your environment.

	 You can create a `.env` file in `backend/` with the variables you need.

4. Run the backend (from repo root):

	 ```bash
	 uvicorn backend.api.app:app --reload
	 ```

	 Notes:
	 - Run uvicorn from the repo root using the `backend.api.app:app` import path to avoid relative-import problems.
	 - Ensure you activate the same virtualenv where you installed packages (langchain adapters, pydantic-settings, etc.).

## Frontend — setup and run

1. Install dependencies and run dev server:

	 ```bash
	 cd frontend
	 npm install
	 # Set VITE_API_URL if your backend runs on a different host/port.
	 export VITE_API_URL=http://127.0.0.1:8000
	 npm run dev
	 ```

2. Build for production:

	 ```bash
	 npm run build
	 ```

3. Configuration

	 - The frontend reads the backend URL from `import.meta.env.VITE_API_URL`. If not set it falls back to `http://127.0.0.1:8000` (development). You can change this in `frontend/src/lib/api.ts` and/or set `VITE_API_URL` in your environment.

## Important files and layout
- `backend/` — FastAPI app and utilities
	- `backend/api/` — FastAPI package (routers, settings, shared singletons)
	- `backend/utils/` — helper scripts (OCR, graph workflows, etc.)
- `frontend/` — React + TypeScript app (Vite)

## Git and local state
- The following are ignored in this repository (already added to `.gitignore`):
	- `chroma_db/` and `backend/chroma_db/` — local Chroma vector DB files
	- `sb-venv/` — local Python virtual environment

If you previously committed these directories and want to stop tracking them now, run from the repo root:

```bash
# remove from index but keep the files locally
git rm --cached -r backend/chroma_db
git rm --cached -r sb-venv
git commit -m "Stop tracking local Chroma DB and virtualenv"
```

## Troubleshooting

- Import errors (e.g. relative imports, `importlib` attribute errors):
	- Ensure you run uvicorn with the module path from the repo root:
		`uvicorn backend.api.app:app --reload`.
	- Activate the correct virtual environment that has the required Python packages installed.

- Pydantic / BaseSettings errors:
	- This project uses Pydantic v2-style settings via `pydantic-settings`. Make sure `pydantic-settings` is installed in the backend venv.

- Frontend hard-coded backend URLs:
	- The frontend centralizes the backend URL in `frontend/src/lib/api.ts`. Set `VITE_API_URL` to override the fallback.

## Developing

- Add new routers under `backend/api/` and register them in `backend/api/app.py`.
- For frontend changes, pages live in `frontend/src/pages/` and shared state is in `frontend/src/contexts/`.

## Contributing

Contributions welcome. Open an issue or create a pull request with a short description of the change.

## License
See the repository `LICENSE` file for license details.
