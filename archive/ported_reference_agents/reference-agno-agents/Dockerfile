FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy local packages (required for dependencies)
COPY packages /packages

# Copy AgentOS requirements
COPY services/agent_os/requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy AgentOS application code
COPY services/agent_os/app /app/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
