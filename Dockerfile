# Use Python slim image as base
FROM python:3.12-slim

# Set environment variables to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    libatk1.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    libgconf-2-4 \
    xdg-utils \
    chromium && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -qO- https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb > google-chrome.deb && \
    dpkg -i google-chrome.deb || apt-get -fy install && \
    rm google-chrome.deb

# Install Chromedriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    wget -q "https://chromedriver.storage.googleapis.com/$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/*

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add Chromedriver to PATH (optional if already installed globally)
ENV PATH="/usr/local/bin:$PATH"

# Make the setup script executable
RUN chmod +x setup.sh

# Start the application
CMD ["./setup.sh"]
