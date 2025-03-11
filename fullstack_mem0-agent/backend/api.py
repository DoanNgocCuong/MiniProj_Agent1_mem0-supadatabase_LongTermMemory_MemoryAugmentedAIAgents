from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from mem0 import Memory
import os
import uuid

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Mem0 API", version="1.0.0")
security = HTTPBearer()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Mem0 Setup
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
        }
    },
    "vector_store": {
        "provider": "supabase",
        "config": {
            "connection_string": os.environ['DATABASE_URL'],
            "collection_name": "memories_fullstack_new",
            "embedding_model_dims": 1536
        }
    }    
}

try:
    memory = Memory.from_config(config)
    print("Successfully created Memory collection")
except Exception as e:
    print(f"Error initializing Memory: {str(e)}")
    # Cung cấp một memory giả để ứng dụng không crash
    # hoặc bạn có thể xử lý tùy theo trường hợp

# Model definitions
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class MemoryRequest(BaseModel):
    user_id: str
    query: str
    limit: int = 3

class MemoryResponse(BaseModel):
    memories: List[Dict[str, Any]]

class UserMessages(BaseModel):
    messages: List[Dict[str, Any]]
    session_id: str

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify bearer token"""
    token = credentials.credentials
    expected_token = os.getenv("API_TOKEN", "mem0-fullstack-token")
    
    # Đầu tiên kiểm tra xem có phải API token không
    if token == expected_token:
        return True
        
    # Nếu không, thử xác thực với Supabase
    try:
        # Verify with Supabase JWT
        user = supabase.auth.get_user(token)
        if user and user.data and user.data.id:
            return True
    except Exception as e:
        print(f"Token verification error: {str(e)}")
    
    # Nếu cả hai đều không thành công, từ chối truy cập
    raise HTTPException(status_code=401, detail="Invalid token")

# API Endpoints
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authenticated: bool = Depends(verify_token)):
    """Generate a chat response with memories"""
    try:
        # Use provided session_id or generate a new one
        session_id = request.session_id or str(uuid.uuid4())
        
        # Search memories
        try:
            relevant_memories = memory.search(query=request.message, user_id=request.user_id, limit=3)
            memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
        except Exception as e:
            print(f"Error retrieving memories: {str(e)}")
            memories_str = "(No memories available)"
        
        # Generate response
        system_prompt = f"You are a helpful AI assistant with memory. Answer based on the query and user's memories.\nUser Memories:\n{memories_str}"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": request.message}]
        
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model=os.getenv('MODEL_CHOICE', 'gpt-4o-mini'),
            messages=messages,
            timeout=60
        )
        assistant_response = response.choices[0].message.content
        
        # Store message in Supabase
        try:
            # Store user message
            supabase.table("messages").insert({
                "session_id": session_id,
                "message": {"type": "human", "content": request.message}
            }).execute()
            
            # Store assistant response
            supabase.table("messages").insert({
                "session_id": session_id,
                "message": {"type": "ai", "content": assistant_response}
            }).execute()
        except Exception as e:
            print(f"Error storing messages: {str(e)}")
        
        # Add to memory
        try:
            memory_messages = [
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": assistant_response}
            ]
            memory.add(memory_messages, user_id=request.user_id)
        except Exception as e:
            print(f"Error adding to memory: {str(e)}")
        
        return ChatResponse(response=assistant_response, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/sessions/{user_id}")
async def get_sessions(user_id: str, authenticated: bool = Depends(verify_token)):
    """Get all sessions for a user"""
    try:
        response = supabase.table("messages").select("session_id").eq("user_id", user_id).execute()
        sessions = set(item["session_id"] for item in response.data)
        return {"sessions": list(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")

@app.get("/api/messages/{session_id}")
async def get_messages(session_id: str, authenticated: bool = Depends(verify_token)):
    """Get all messages for a session"""
    try:
        response = supabase.table("messages").select("*").eq("session_id", session_id).order("created_at").execute()
        return {"messages": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")

@app.post("/api/memories/search", response_model=MemoryResponse)
async def search_memories(request: MemoryRequest, authenticated: bool = Depends(verify_token)):
    """Search memories for a user"""
    try:
        results = memory.search(query=request.query, user_id=request.user_id, limit=request.limit)
        return MemoryResponse(memories=results["results"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching memories: {str(e)}")

@app.delete("/api/memories/{user_id}")
async def clear_memories(user_id: str, authenticated: bool = Depends(verify_token)):
    """Clear all memories for a user"""
    try:
        memory.clear(user_id=user_id)
        return {"success": True, "message": "Memories cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memories: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 