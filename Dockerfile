FROM python:3.11-slim

# Install system dependencies for PyPlatec and h5py
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    gcc \
    g++ \
    libhdf5-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all project files
COPY . /app/

# Install worldengine with dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e ".[hdf5,dev]"

# Default command
CMD ["worldengine", "--help"]
