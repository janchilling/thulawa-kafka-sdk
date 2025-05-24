# Use an official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the required files to the container
COPY requirements.txt .
# Ensure your Python script is named correctly
COPY auto_scaler.py .  

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (if needed)
ENV PROMETHEUS_URL=http://prometheus.streamspace.svc.cluster.local:9090
ENV DEPLOYMENT_NAME=kafka-streams-app
ENV NAMESPACE=streamspace

# Command to run the auto_scaler script
CMD ["python", "auto_scaler.py"]
