# Use a base image with Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install jq, node, and npm
RUN apt-get update && apt-get install -y jq nodejs npm

# Make the script executable
RUN chmod +x /app/run.sh

# Set environment variable (or set it during docker run)
ENV MONGO_CONNECTION_STRING="your_connection_string"

# Run the script in the background every 6 hours
CMD ["sh", "-c", "while true; do /app/run.sh; sleep 21600; done"]
