# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

SHELL ["/bin/bash", "-c"]
# Install system dependencies
RUN apt-get update && apt-get install -y libwebkit2gtk-4.0-dev build-essential curl wget file libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev

# Install Rust
RUN curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y

#RUN export PATH="$HOME/.cargo/bin:$PATH"
ENV PATH="$PATH:/root/.cargo/bin"
RUN echo $PATH

# Install Python dependencies
COPY /software-inventory-api/requirements.txt .
RUN pip install -r requirements.txt

# Copy the Tauri project files into the container
COPY software-inventory /app/software-inventory
COPY software-inventory-api /app/software-inventory-api

# Install Node.js and npm for building the frontend
ENV NODE_VERSION=16.13.0
RUN apt install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | sh
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version

RUN apt-get install -y nodejs
RUN cd /app/software-inventory && npm install
RUN source ~/.bashrc
#RUN cd /app/software-inventory && npm run tauri dev

# Expose the port for the Python backend
EXPOSE 8000
EXPOSE 3000

ENV DISPLAY=:0

# Change working directory to the backend
WORKDIR /app/software-inventory-api

#CMD  printenv && rustc --version && cargo --version 
# Define the command to start the combined application
CMD cd /app/software-inventory && pwd && npm run tauri dev & \ 
   cd /app/software-inventory-api && uvicorn main:app --host 0.0.0.0 --port 8000 & \
   tail -f /dev/null

