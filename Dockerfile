# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    mlocate \
    locate \
    && rm -rf /var/lib/apt/lists/*

# Update locate database
RUN updatedb

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Install ochrona
RUN pip install ochrona

# Copy the entire project
COPY . .

# Set environment variable to use host network (for connecting to local MongoDB)
ENV MONGODB_URI=${MONGODB_URI}
ENV MONGODB_DB=${MONGODB_DB}

# Expose the FastAPI port
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'python scripts/python_environments.py' >> /app/start.sh && \
    echo 'python scripts/node_environments.py' >> /app/start.sh && \
    echo 'uvicorn main:app --host 0.0.0.0 --port 8000' >> /app/start.sh && \
    chmod +x /app/start.sh

# Command to run the application
CMD ["/bin/bash", "/app/start.sh"]