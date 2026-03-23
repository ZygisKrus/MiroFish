# Build Frontend
FROM --platform=linux/amd64 node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Runtime Stage
FROM --platform=linux/amd64 python:3.11-slim
WORKDIR /app

# Install system dependencies (Node is needed for npm run backend)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy backend dependency files only (to protect cache)
COPY backend/pyproject.toml backend/uv.lock ./backend/

# Install Backend dependencies (large AI libraries)
RUN cd backend && uv sync --frozen

# Copy root package files (scripts for running the app)
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Copy source code
COPY . .

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure uploads and logs directories exist
RUN mkdir -p backend/uploads backend/logs

EXPOSE 3000 5001

CMD ["npm", "run", "backend"]