# Frontend build stage
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Serve static files — output in /app/dist
FROM scratch AS frontend-dist
COPY --from=frontend-build /app/dist /
