# Use a base image that includes Python (e.g., python:3.11-bullseye)
FROM python:3.10-bullseye

# Copy your application code
COPY ./learnhearCore /learnhearCore

WORKDIR /learnhearCore
# Update and install system-level dependencies
RUN apt-get update && apt-get install -y python3-pip

# Install Python packages and dependencies
RUN pip install --upgrade pip setuptools
RUN pip install git+https://github.com/suno-ai/bark.git
RUN pip install git+https://github.com/huggingface/transformers.git

# Install PyTorch, torchvision, and torchaudio with CUDA 11.8
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Set the working directory for your application

# Copy and install project dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt



# Copy entrypoint script
COPY ./entrypoint.sh /

# Set the entrypoint script as the default command

ENTRYPOINT ["sh", "/entrypoint.sh"]
