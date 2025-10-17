FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app/app

# Copy training script
COPY train.py /app/train.py

# Create directories for data and models
RUN mkdir -p /app/data /app/models

# Create kaggle config directory and copy credentials
RUN mkdir -p /root/.kaggle
COPY kaggle.json /root/.kaggle/kaggle.json
RUN chmod 600 /root/.kaggle/kaggle.json

# Expose port
EXPOSE 8001

# Start script that checks for model and trains if needed, then starts API
CMD python app/startup.py && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload