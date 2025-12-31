FROM nginx:latest
WORKDIR /usr/share/nginx/html
RUN rm -rf *
COPY . .
RUN sed -i 's|http://localhost:8001|/|g' index.html 2>/dev/null || true
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
