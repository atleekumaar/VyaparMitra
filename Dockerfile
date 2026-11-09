# Multi-stage Dockerfile for VyaparMitra Production Command Center

# --- Stage 1: Build Frontend Assets ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Python Application ---
FROM python:3.12-slim AS runner
WORKDIR /app

# Set production environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    API_HOST=0.0.0.0 \
    API_PORT=8000

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code, intelligence data marts, configurations, and ML models
COPY src/ ./src/
COPY data/ ./data/
COPY configs/ ./configs/
COPY models/ ./models/

# Copy built frontend assets from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose HTTP port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Run the API server
CMD ["python", "-m", "src.api"]
