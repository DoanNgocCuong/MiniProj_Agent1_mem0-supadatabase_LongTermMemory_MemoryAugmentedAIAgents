#!/bin/bash

# Tạo thư mục cần thiết
mkdir -p frontend/public
mkdir -p frontend/src/components
mkdir -p frontend/src/services

# Copy các file đã tạo
# Các file đã có

# Tạo các thư mục rỗng nếu cần
mkdir -p frontend/public/assets

# Tạo favicon đơn giản (1x1 pixel transparent)
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" | base64 -d > frontend/public/favicon.ico

echo "Khởi tạo frontend hoàn tất!"
echo "Chạy lệnh 'docker-compose up --build -d' để bắt đầu" 