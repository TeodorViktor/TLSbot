FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make the setup script executable
RUN chmod +x /app/setup.sh

# Expose the required port (if any)
EXPOSE 8000

# Run the script
CMD ["./setup.sh"]
