# syntax=docker/dockerfile:1.7

FROM node:18-alpine
WORKDIR /app

# 安裝基本套件與 corepack (for pnpm)
RUN apk add --no-cache libc6-compat && corepack enable

# 加入環境變數，避免 pnpm 互動問題
ENV CI=true

# 複製檔案
COPY app ./app
COPY blueprints ./blueprints
COPY meta.json ./meta.json

WORKDIR /app/app

# 安裝依賴
RUN pnpm install

# 暴露 Vite dev server port
EXPOSE 47291

# 啟動 Vite 開發伺服器
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0", "--port", "47291"]
