FROM nginx:latest

# Copy HTML files to nginx html directory
COPY index.html /usr/share/nginx/html/
COPY css /usr/share/nginx/html/css/
COPY js /usr/share/nginx/html/js/
COPY assets /usr/share/nginx/html/assets/

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Replace localhost:8001 references with / for API calls
RUN sed -i 's|http://localhost:8001|http://amparo_backend:8000|g' /usr/share/nginx/html/index.html 2>/dev/null || true
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
