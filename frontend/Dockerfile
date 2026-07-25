# CPQ Agent Frontend — Nginx + 静态文件 + API 反向代理
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
