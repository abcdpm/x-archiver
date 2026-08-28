# =================阶段 1: 构建前端=================
FROM node:20-alpine AS builder

WORKDIR /app

# 利用 Docker 缓存层加速 npm install
COPY package*.json ./
RUN npm install

# 复制源代码并进行 Vite 构建
COPY . .
RUN npm run build

# =================阶段 2: Nginx 静态服务=================
FROM nginx:alpine

# 清理 Nginx 默认的 html 内容
RUN rm -rf /usr/share/nginx/html/*

# 从 builder 阶段复制打包产物(dist)到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露 Nginx 默认端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]