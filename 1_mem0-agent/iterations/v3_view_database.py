import os
import streamlit as st
from dotenv import load_dotenv
import supabase
import pandas as pd
import time
import psycopg2
from psycopg2 import sql

# Load environment variables
load_dotenv()

# Initialize constants
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
DB_URL = os.environ.get("DATABASE_URL", "")

# Streamlit page configuration
st.set_page_config(
    page_title="Memory Database Explorer",
    page_icon="🔍",
    layout="wide"
)

# Sidebar with author information
with st.sidebar:
    st.title("Database Explorer")
    
    # Author information
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("baby.png", width=60)
    with col2:
        st.markdown("### Doan Ngoc Cuong")
        st.markdown("[GitHub Profile](https://github.com/DoanNgocCuong)")
    st.markdown("---")

# Main title
st.title("Memory Database Explorer")

# Initialize connection
try:
    # Initialize Supabase client
    supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
    st.success("Connected to Supabase!")
    
    # Show connection information
    st.write(f"Connection details:")
    st.write(f"- Supabase URL: {SUPABASE_URL[:20]}...")
    st.write(f"- Database URL exists: {'Yes' if DB_URL else 'No'}")
except Exception as e:
    st.error(f"Failed to connect to Supabase: {str(e)}")

# Direct PostgreSQL connection
try:
    if DB_URL:
        conn = psycopg2.connect(DB_URL)
        st.success("Direct PostgreSQL connection established!")
        
        # Find all tables in all schemas
        with conn.cursor() as cur:
            # Query to get all tables from all schemas
            cur.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name
            """)
            tables = cur.fetchall()
            
            if tables:
                st.subheader("All Tables in Database")
                table_options = [f"{schema}.{table}" for schema, table in tables]
                selected_table = st.selectbox("Select a table to view", table_options)
                
                if selected_table:
                    schema, table = selected_table.split('.')
                    
                    # Get data from the selected table
                    cur.execute(
                        sql.SQL("SELECT * FROM {}.{} LIMIT 100").format(
                            sql.Identifier(schema),
                            sql.Identifier(table)
                        )
                    )
                    
                    # Get column names
                    columns = [desc[0] for desc in cur.description]
                    
                    # Fetch data
                    data = cur.fetchall()
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(data, columns=columns)
                    
                    # Display the data
                    st.subheader(f"Contents of {selected_table}")
                    st.write(f"Found {len(df)} records")
                    st.dataframe(df, use_container_width=True)
                    
                    # Look for vecs collections
                    if "metadata" in df.columns:
                        st.subheader("Extracted Metadata")
                        
                        # Process metadata
                        formatted_data = []
                        for _, row in df.iterrows():
                            try:
                                metadata = row.get("metadata")
                                if metadata:
                                    formatted_row = {"id": row.get("id", "")}
                                    
                                    # Try to extract fields from metadata
                                    if isinstance(metadata, dict):
                                        formatted_row["user_id"] = metadata.get("user_id", "")
                                        formatted_row["memory"] = metadata.get("memory", "")
                                    
                                    formatted_data.append(formatted_row)
                            except Exception as e:
                                st.error(f"Error processing row: {str(e)}")
                        
                        if formatted_data:
                            formatted_df = pd.DataFrame(formatted_data)
                            st.dataframe(formatted_df, use_container_width=True)
                    
                    # Check for special vecs tables
                    vecs_tables = [t for t in table_options if 'vecs' in t.lower()]
                    if vecs_tables:
                        st.subheader("Vector Collection Tables")
                        st.write("These tables might be used by mem0:")
                        for vt in vecs_tables:
                            st.write(f"- {vt}")
            else:
                st.warning("No tables found in database")
    else:
        st.error("DATABASE_URL environment variable is missing")
except Exception as e:
    st.error(f"Error accessing PostgreSQL directly: {str(e)}")

# Add refresh button
if st.button("Refresh"):
    st.rerun() 