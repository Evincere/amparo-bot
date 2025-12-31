FROM public.ecr.aws/docker/library/nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY . /usr/share/nginx/html/
RUN sed -i 's|http://localhost:8001|/|g' /usr/share/nginx/html/index.html 2>/dev/null || true
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
