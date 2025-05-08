FROM node:18-alpine as build

WORKDIR /app

# Chỉ copy package.json trước (không cần package-lock.json)
COPY package.json ./

# Cài đặt dependencies và tạo package-lock.json
RUN npm install

# Copy source code
COPY . .

# Build app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Add nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 