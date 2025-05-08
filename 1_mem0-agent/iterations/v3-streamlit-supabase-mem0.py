import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from mem0 import Memory
import supabase
from supabase.client import Client, ClientOptions
import uuid
import vecs
import psycopg2

# Load environment variables
load_dotenv()

# Initialize constants
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
MODEL_CHOICE = os.environ.get("MODEL_CHOICE", "gpt-4o-mini")

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL", "https://gewcfncoqvxnkrbpfonk.supabase.co")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase_client = supabase.create_client(supabase_url, supabase_key)

# Streamlit page configuration
st.set_page_config(
    page_title="Mem0 Chat Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client
client = OpenAI()

# Cache OpenAI client and Memory instance
@st.cache_resource
def get_openai_client():
    return OpenAI()

@st.cache_resource
def get_memory():
    try:
        # Kết nối trực tiếp để tăng timeout
        conn_str = os.environ['DATABASE_URL']
        
        # Tăng statement_timeout cho toàn bộ phiên
        try:
            direct_conn = psycopg2.connect(conn_str)
            with direct_conn.cursor() as cur:
                # Tăng statement_timeout lên 5 phút
                cur.execute("SET statement_timeout = 300000")  # 5 phút
                direct_conn.commit()
            
            # Sửa đổi chuỗi kết nối để thêm options
            if "?" in conn_str:
                conn_str += "&options=--statement_timeout=300000"
            else:
                conn_str += "?options=--statement_timeout=300000"
                
            direct_conn.close()
        except Exception as e:
            st.warning(f"Không thể cấu hình timeout: {str(e)}")
        
        # Tạo config cho Memory - loại bỏ create_collection
        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": MODEL_CHOICE
                }
            },
            "vector_store": {
                "provider": "supabase",
                "config": {
                    "connection_string": conn_str,
                    "collection_name": "memories_new",
                    "embedding_model_dims": 1536  # Số chiều của OpenAI text-embedding-ada-002
                }
            }    
        }
        
        # Thử tạo collection trước khi khởi tạo Memory
        try:
            import vecs
            db = vecs.create_client(conn_str)
            # Kiểm tra nếu collection đã tồn tại
            try:
                # Sử dụng get_or_create_collection thay vì create_collection
                db.get_or_create_collection(
                    name="memories_new",
                    dimension=1536
                )
                st.success("Collection đã được tạo/truy cập thành công!")
            except Exception as e:
                st.warning(f"Không thể tạo collection: {str(e)}")
        except Exception as e:
            st.warning(f"Không thể kết nối với vecs: {str(e)}")
        
        return Memory.from_config(config)
    except Exception as e:
        st.error(f"Lỗi khởi tạo Memory: {str(e)}")
        # Trả về đối tượng giả
        class FallbackMemory:
            def search(self, query, user_id, limit=3):
                return {"results": []}
            def add(self, messages, user_id):
                pass
            def clear(self, user_id):
                pass
        return FallbackMemory()

# Get cached resources
openai_client = get_openai_client()
memory = get_memory()

# Authentication functions
def sign_up(email, password, full_name):
    try:
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })
        if response and response.user:
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.rerun()
        return response
    except Exception as e:
        st.error(f"Error signing up: {str(e)}")
        return None

def sign_in(email, password):
    try:
        response = supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response and response.user:
            # Store user info directly in session state
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.rerun()
        return response
    except Exception as e:
        st.error(f"Error signing in: {str(e)}")
        return None

def sign_out():
    try:
        supabase_client.auth.sign_out()
        # Clear only authentication-related session state
        st.session_state.authenticated = False
        st.session_state.user = None
        # Set a flag to trigger rerun on next render
        st.session_state.logout_requested = True
    except Exception as e:
        st.error(f"Error signing out: {str(e)}")

# Chat function with memory
def chat_with_memories(message, user_id):
    try:
        # Retrieve relevant memories
        with st.spinner("Searching memories..."):
            try:
                relevant_memories = memory.search(query=message, user_id=user_id, limit=3)
                memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
            except Exception as e:
                st.error(f"Error retrieving memories: {str(e)}")
                memories_str = "(No memories available)"
        
        # Generate Assistant response
        system_prompt = f"You are a helpful AI assistant with memory. Answer the question based on the query and user's memories.\nUser Memories:\n{memories_str}"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]
        
        with st.spinner("Thinking..."):
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=messages,
                    timeout=60  # Increase timeout to 60 seconds
                )
                assistant_response = response.choices[0].message.content
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                return "I'm sorry, I couldn't generate a response at this time. Please try again later."

        # Create new memories from the conversation
        try:
            messages.append({"role": "assistant", "content": assistant_response})
            memory.add(messages, user_id=user_id)
        except Exception as e:
            st.warning(f"Could not save this conversation to memory: {str(e)}")

        return assistant_response
    except Exception as e:
        st.error(f"General error: {str(e)}")
        return "Sorry, an error occurred. Please try again later."

# Initialize session state
if not st.session_state.get("messages", None):
    st.session_state.messages = []

if not st.session_state.get("authenticated", None):
    st.session_state.authenticated = False

if not st.session_state.get("user", None):
    st.session_state.user = None

# Check for logout flag and clear it after processing
if st.session_state.get("logout_requested", False):
    st.session_state.logout_requested = False
    st.rerun()

# Sidebar for authentication
with st.sidebar:
    st.title("🧠 Mem0 Chat")
    
    # Thêm thông tin tác giả
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("baby.png", width=60)
    with col2:
        st.markdown("### Doan Ngoc Cuong")
        st.markdown("[GitHub Profile](https://github.com/DoanNgocCuong)")
    st.markdown("---")
    
    if not st.session_state.authenticated:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Login")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_button = st.button("Login")
            
            if login_button:
                if login_email and login_password:
                    sign_in(login_email, login_password)
                else:
                    st.warning("Please enter both email and password.")
        
        with tab2:
            st.subheader("Sign Up")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_name = st.text_input("Full Name", key="signup_name")
            signup_button = st.button("Sign Up")
            
            if signup_button:
                if signup_email and signup_password and signup_name:
                    response = sign_up(signup_email, signup_password, signup_name)
                    if response and response.user:
                        st.success("Sign up successful! Please check your email to confirm your account.")
                    else:
                        st.error("Sign up failed. Please try again.")
                else:
                    st.warning("Please fill in all fields.")
    else:
        user = st.session_state.user
        if user:
            st.success(f"Logged in as: {user.email}")
            st.button("Logout", on_click=sign_out)
            
            # Display user information
            st.subheader("Your Profile")
            st.write(f"User ID: {user.id}")
            
            # Memory management options
            st.subheader("Memory Management")
            if st.button("Clear All Memories"):
                memory.clear(user_id=user.id)
                st.success("All memories cleared!")
                st.session_state.messages = []
                st.rerun()

# Main chat interface
if st.session_state.authenticated and st.session_state.user:
    # Use the user from session state directly
    user_id = st.session_state.user.id
    
    st.title("Chat with Memory-Powered AI")
    st.write("Your conversation history and preferences are remembered across sessions.")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get AI response
        ai_response = chat_with_memories(user_input, user_id)
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # Display AI response
        with st.chat_message("assistant"):
            st.write(ai_response)
else:
    st.title("Welcome to Mem0 Chat Assistant")
    st.write("Please login or sign up to start chatting with the memory-powered AI assistant.")
    st.write("This application demonstrates how AI can remember your conversations and preferences over time.")
    
    # Feature highlights
    st.subheader("Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🧠 Long-term Memory")
        st.write("The AI remembers your past conversations and preferences.")
    
    with col2:
        st.markdown("### 🔒 Secure Authentication")
        st.write("Your data is protected with Supabase authentication.")
    
    with col3:
        st.markdown("### 💬 Personalized Responses")
        st.write("Get responses tailored to your history and context.")

if __name__ == "__main__":
    # This section won't run in Streamlit
    pass
