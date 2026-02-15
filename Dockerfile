# Stage 1: Build Frontend
FROM node:18-alpine as frontend_build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Backend
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy Backend Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend Code
COPY src/ src/
COPY data/ data/

# Copy Frontend Build from Stage 1
COPY --from=frontend_build /app/frontend/dist /app/frontend/dist

# Expose Port
EXPOSE 5000

# Run Flask Configuration
# Note: We need to make sure flask_app.py knows where to look for static files
# In our code we set static_folder="../../frontend/dist"
# So if we run from /app, and src is at /app/src, then ../../frontend/dist is /frontend/dist
# But wait, flask_app.py is in /app/src/api/flask_app.py
# So os.path.dirname is /app/src/api
# dirname(dirname) is /app/src
# dirname(dirname(dirname)) is /app
# So BASE_DIR is /app
# We need frontend/dist to be at /app/frontend/dist. This matches.

ENV PYTHONUNBUFFERED=1
ENV PORT=5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "src.api.flask_app:app"]
