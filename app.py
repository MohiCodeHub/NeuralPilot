from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from neuralpilot.model import Model
from session_manager import create_session, clear_context,get_context,update_context


app = FastAPI()
model = Model()
templates = Jinja2Templates(directory = "templates")

# Mount static files for CSS
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/", response_class = HTMLResponse)
def root(request : Request):
    return templates.TemplateResponse("index.html", {"request" : request})

@app.get("/chat", response_class = HTMLResponse)
def chat(request : Request):
    session_id = create_session()
    return templates.TemplateResponse("chat.html", {"request" : request, "session_id" : session_id})

@app.post("/chat",response_class = JSONResponse)
async def chat(request : Request):
    response = await request.json()
    session_id = response["session_id"]
    user_msg = response["message"]

    context = get_context(session_id)
    response = model.get_output(user_msg, context)
    update_context(session_id, user_msg, response)

    return JSONResponse({"response" : response})










