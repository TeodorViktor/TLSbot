# Install dependencies
apt-get update && apt-get install -y \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxext6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    fonts-liberation \
    xdg-utils

# Clean up
apt-get clean && rm -rf /var/lib/apt/lists/*
#!/bin/bash
python3 main.py