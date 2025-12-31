FROM public.ecr.aws/docker/library/nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy static assets
COPY . /usr/share/nginx/html

# Replace localhost API URL with relative path for Nginx proxying
# This changes 'http://localhost:8001' to '' so requests go to /api/chat/stream
RUN sed -i 's|http://localhost:8001||g' /usr/share/nginx/html/index.html
RUN sed -i 's|backend|amparobot-backend-fnpbys|g' /usr/share/nginx/html/nginx.confconf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
