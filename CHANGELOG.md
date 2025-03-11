# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 12-03-2025

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

### Trong version này thì mới có: mem0-agent/iterations/v3...
- Gồm có v3_view_database và v3-streamlit-app
- Chưa xong full_stack-mem0-agent
- Đã test mem0-agent/studio-integration-version nhưng cái này chỉ là API Fast API thui

How Run: 
```
cd mem0-agent/iterations
sudo docker compose up -build --d
```

--------------------------------