# Build stage
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM public.ecr.aws/docker/library/nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html/

# Replace localhost API URL with relative path for Nginx proxying
# This changes 'http://localhost:8001' to '/' so requests go to /api/chat/stream
RUN sed -i 's|http://localhost:8001|/|g' /usr/share/nginx/html/index.html
RUN sed -i 's|backend|amparobot-backend-fnpbys|g' /usr/share/nginx/html/nginx.conf 2>/dev/null || true

# Copy custom Nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf 2>/dev/null || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
