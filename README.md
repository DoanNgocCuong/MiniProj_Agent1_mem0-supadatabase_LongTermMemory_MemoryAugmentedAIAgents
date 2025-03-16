# mem0-supadatabase - Đoàn Ngọc Cường 

Link repo: https://github.com/coleam00/ottomator-agents/tree/main/mem0-agent

============
<think>
Let me create a comprehensive README and CHANGELOG for this project. I'll structure it professionally to describe the project, its features, installation instructions, and usage.

For the README, I'll include:
1. Project overview
2. Features
3. Installation instructions
4. Usage
5. Configuration
6. Docker deployment
7. License and credits

For the CHANGELOG, I'll create an initial entry for the 1.0 release with all the features that have been implemented.
</think>

# Mem0 Chat Assistant with Database Viewer

## Release 1.0

A fullstack application featuring a memory-powered AI chat assistant built with Streamlit, Supabase vector storage, and OpenAI. This project demonstrates how AI can maintain context and remember past conversations across sessions using vector embeddings.

![Mem0 Chat Assistant](screenshot.png)

## Features

### 🧠 Memory-Powered Chat
- Long-term memory storage using vector embeddings
- Contextual responses based on conversation history
- Memory persistence across sessions

### 🔍 Database Explorer
- View and explore the vector database 
- Browse all tables in all schemas
- Examine memory contents and metadata

### 🔒 User Authentication
- Secure login and registration using Supabase
- User-specific memories and conversations
- Profile management

### 🔧 Technical Features
- Vector embedding storage for semantic search
- Containerized deployment with Docker
- Error handling and graceful degradation

## Quick Start

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/DoanNgocCuong/mem0-supadatabase.git
cd mem0-supadatabase

# Configure your environment variables
cp .env.example .env
# Edit .env with your Supabase and OpenAI credentials

# Start the applications
docker-compose up -d
```

### Accessing the Applications
- Chat Application: http://localhost:25048
- Database Viewer: http://localhost:25049

## Configuration

Edit the `.env` file to configure the following:

```
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DATABASE_URL=your_database_connection_string
MODEL_CHOICE=gpt-4o-mini  # or another OpenAI model
```

## Architecture

This project consists of two main components:

1. **Mem0 Chat Assistant**: A Streamlit application that provides a chat interface with memory-powered responses.
2. **Database Viewer**: A separate Streamlit application for exploring the vector database.

Both components connect to the same Supabase backend for data storage and authentication.

## Development

### Requirements
- Python 3.10+
- Supabase account
- OpenAI API key

### Local Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the applications
streamlit run v3-streamlit-supabase-mem0.py
streamlit run v3_view_database.py
```

## Troubleshooting

### Common Issues

- **Database Timeout**: Increase PostgreSQL statement_timeout value
- **Authentication Issues**: Ensure Supabase credentials are correct
- **Memory Creation Error**: Check database connection and permissions

## Credits

Developed by [Doan Ngoc Cuong](https://github.com/DoanNgocCuong)

Based on the [Ottomator Mem0 Agent](https://github.com/coleam00/ottomator-agents/tree/main/mem0-agent)

## License

MIT License

```markdown:CHANGELOG.md
# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-03-30

### Added
- Initial release of Mem0 Chat Assistant
- Memory-powered conversations using vector embeddings
- User authentication with Supabase
- Database viewer for exploring vector storage
- Docker containerization for both applications
- Profile information display for logged in users
- Memory management features (search, add, clear)
- Error handling and graceful degradation
- Configurable OpenAI model selection
- Real-time chat interface with message history
- Author information and GitHub profile link

### Fixed
- PostgreSQL timeout issues with increased timeouts
- Memory collection creation with proper error handling
- Database connection stability across container restarts
- Authentication session persistence
- Metadata extraction and display in Database Viewer
```

Is there anything specific you'd like me to add to the README or CHANGELOG?
