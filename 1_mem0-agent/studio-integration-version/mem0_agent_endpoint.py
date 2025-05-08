from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from mem0 import Memory
import httpx
import sys
import os

from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    TextPart
)

from mem0_agent import mem0_agent, Mem0Deps

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
security = HTTPBearer()

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
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Mem0 Setup
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": os.getenv('LLM_MODEL', 'gpt-4o-mini')
        }
    },
    "vector_store": {
        "provider": "supabase",
        "config": {
            "connection_string": os.environ['DATABASE_URL'],
            "collection_name": "memories_api_new",
            "embedding_model_dims": 1536
        }
    }    
}

try:
    memory = Memory.from_config(config)
    print(f"Successfully created collection with config: {config}")
except Exception as e:
    print(f"Failed to create collection: {str(e)}")
    # Thử lại với cách khác nếu lỗi
    try:
        alt_config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": os.getenv('LLM_MODEL', 'gpt-4o-mini')
                }
            }
        }
        memory = Memory.from_config(alt_config)
        print("Using fallback in-memory storage")
    except Exception as e2:
        print(f"Failed to create fallback memory: {str(e2)}")
        # Tiếp tục khởi động API mà không có memory

# Request/Response Models
class AgentRequest(BaseModel):
    query: str
    user_id: str
    request_id: str
    session_id: str

class AgentResponse(BaseModel):
    success: bool

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify the bearer token against environment variable."""
    expected_token = os.getenv("API_BEARER_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="API_BEARER_TOKEN environment variable not set"
        )
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return True    

async def fetch_conversation_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent conversation history for a session."""
    try:
        response = supabase.table("messages") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        # Convert to list and reverse to get chronological order
        messages = response.data[::-1]
        return messages
    except Exception as e:
        print(f"Error fetching conversation history: {str(e)}")
        return []

async def store_message(session_id: str, message_type: str, content: str, data: Optional[Dict] = None):
    """Store a message in the Supabase messages table."""
    message_obj = {
        "type": message_type,
        "content": content
    }
    if data:
        message_obj["data"] = data

    try:
        supabase.table("messages").insert({
            "session_id": session_id,
            "message": message_obj
        }).execute()
        print(f"Stored message: {message_type} - {content[:30]}...")
    except Exception as e:
        print(f"Failed to store message: {str(e)}")

@app.post("/api/mem0-agent", response_model=AgentResponse)
async def web_search(
    request: AgentRequest,
    authenticated: bool = Depends(verify_token)
):
    try:
        # Fetch conversation history
        conversation_history = await fetch_conversation_history(request.session_id)
        
        # Convert conversation history to format expected by agent
        messages = []
        for msg in conversation_history:
            msg_data = msg["message"]
            msg_type = msg_data["type"]
            msg_content = msg_data["content"]
            msg = ModelRequest(parts=[UserPromptPart(content=msg_content)]) if msg_type == "human" else ModelResponse(parts=[TextPart(content=msg_content)])
            messages.append(msg)

        # Store user's query
        await store_message(
            session_id=request.session_id,
            message_type="human",
            content=request.query
        )       

        # Retrieve relevant memories with Mem0
        try:
            relevant_memories = memory.search(query=request.query, user_id=request.user_id, limit=3)
            memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
        except Exception as e:
            print(f"Error retrieving memories: {str(e)}")
            memories_str = "(No memories available)"

        # Initialize agent dependencies
        async with httpx.AsyncClient() as client:
            deps = Mem0Deps(
                memories=memories_str
            )

            # Run the agent with conversation history
            result = await mem0_agent.run(
                request.query,
                message_history=messages,
                deps=deps
            )

        # Store agent's response
        await store_message(
            session_id=request.session_id,
            message_type="ai",
            content=result.data,
            data={"request_id": request.request_id}
        )

        # Update memories based on the last user message and agent response
        try:
            memory_messages = [
                {"role": "user", "content": request.query},
                {"role": "assistant", "content": result.data}
            ]
            memory.add(memory_messages, user_id=request.user_id)        
        except Exception as e:
            print(f"Error adding memory: {str(e)}")

        return AgentResponse(success=True)

    except Exception as e:
        print(f"Error processing agent request: {str(e)}")
        # Store error message in conversation
        await store_message(
            session_id=request.session_id,
            message_type="ai",
            content="I apologize, but I encountered an error processing your request.",
            data={"error": str(e), "request_id": request.request_id}
        )
        return AgentResponse(success=False)

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.get("/api/history")
async def get_history(
    session_id: str,
    limit: int = 50,
    authenticated: bool = Depends(verify_token)
):
    """Get conversation history for a session."""
    try:
        messages = await fetch_conversation_history(session_id, limit)
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversation history: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
