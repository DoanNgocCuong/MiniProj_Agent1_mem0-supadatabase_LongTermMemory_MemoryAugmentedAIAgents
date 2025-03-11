from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uuid
import os
import httpx
from pathlib import Path

app = FastAPI()

# Tạo thư mục templates và static
templates_dir = Path("./templates")
templates_dir.mkdir(exist_ok=True)
static_dir = Path("./static")
static_dir.mkdir(exist_ok=True)

# Tạo file CSS cơ bản
css_file = static_dir / "style.css"
if not css_file.exists():
    with open(css_file, "w") as f:
        f.write("""
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { display: flex; flex-direction: column; }
        .message { padding: 10px; margin: 5px 0; border-radius: 10px; max-width: 70%; }
        .user { background-color: #e6f7ff; align-self: flex-end; }
        .ai { background-color: #f0f0f0; align-self: flex-start; }
        form { display: flex; margin-top: 20px; }
        input[type="text"] { flex-grow: 1; padding: 10px; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; }
        """)

# Tạo template HTML
templates_dir.mkdir(exist_ok=True)
index_html = templates_dir / "index.html"
if not index_html.exists():
    with open(index_html, "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mem0 Chat</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <h1>🧠 Mem0 Chat Interface</h1>
            
            <div class="chat-container">
                {% for message in messages %}
                    <div class="message {{ message.type }}">{{ message.content }}</div>
                {% endfor %}
            </div>
            
            <form method="post">
                <input type="text" name="message" placeholder="Type your message..." required>
                <button type="submit">Send</button>
            </form>
        </body>
        </html>
        """)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Initialize or get session
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))
    user_id = request.cookies.get("user_id", str(uuid.uuid4()))
    
    # Get message history from mem0_agent_endpoint API
    messages = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8001/api/history?session_id={session_id}",
                headers={"Authorization": f"Bearer {os.getenv('API_BEARER_TOKEN', 'mem0-secret-token')}"}
            )
            if response.status_code == 200:
                data = response.json()
                for msg in data:
                    msg_data = msg["message"]
                    messages.append({
                        "type": "user" if msg_data["type"] == "human" else "ai",
                        "content": msg_data["content"]
                    })
    except Exception as e:
        print(f"Error fetching message history: {e}")
    
    # Return template with message history
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "messages": messages}
    )

@app.post("/", response_class=HTMLResponse)
async def post_message(request: Request, message: str = Form(...)):
    # Get session info
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))
    user_id = request.cookies.get("user_id", str(uuid.uuid4()))
    
    # Send message to mem0_agent_endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/api/mem0-agent",
                json={
                    "query": message,
                    "user_id": user_id,
                    "session_id": session_id,
                    "request_id": str(uuid.uuid4())
                },
                headers={"Authorization": f"Bearer {os.getenv('API_BEARER_TOKEN', 'mem0-secret-token')}"}
            )
    except Exception as e:
        print(f"Error sending message to API: {e}")
    
    # Get updated message history
    messages = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8001/api/history?session_id={session_id}",
                headers={"Authorization": f"Bearer {os.getenv('API_BEARER_TOKEN', 'mem0-secret-token')}"}
            )
            if response.status_code == 200:
                data = response.json()
                for msg in data:
                    msg_data = msg["message"]
                    messages.append({
                        "type": "user" if msg_data["type"] == "human" else "ai",
                        "content": msg_data["content"]
                    })
    except Exception as e:
        print(f"Error fetching message history: {e}")
    
    # Add the new messages if history API failed
    if not messages:
        messages = [
            {"type": "user", "content": message},
            {"type": "ai", "content": "I received your message but couldn't retrieve the full conversation history."}
        ]
    
    # Return template with updated messages
    response = templates.TemplateResponse(
        "index.html", 
        {"request": request, "messages": messages}
    )
    
    # Set cookies
    response.set_cookie(key="session_id", value=session_id)
    response.set_cookie(key="user_id", value=user_id)
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 