# Use CUDA base image with Ubuntu 20.04
FROM nvidia/cuda:12.1.1-runtime-ubuntu20.04
ENV DEBIAN_FRONTEND noninteractive

# Install Python 3.9 and required dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-distutils \
    python3-pip \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-tk \
    python3-yaml \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.9 as the default
RUN ln -sf /usr/bin/python3.9 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Upgrade pip
RUN pip install --upgrade pip

# Install PyTorch and CUDA-specific packages
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cu121 torch~=2.2.0 torchvision~=0.17.0

# Install other dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Set the default command
CMD ["python", "main.py"]
