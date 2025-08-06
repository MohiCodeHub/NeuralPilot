A chatbot that uses OpenAI's GPT-4o along with RAG using a vector database comprised of up-to-date ML papers from the ArXiv database.
Deployed as a web app using FastAPI.

```markdown
neuralpilot/
├── model.py           # LLM & RAG logic
├── app/               # FastAPI routes
├── data/              # Embedded vectors and raw data
├── scripts/           # One-off scripts (downloading data, chunking, and embedding)
├── templates/         # Frontend features: HTML templates, CSS files, and JS.


