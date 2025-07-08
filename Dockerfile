# FILE: ~/BittyScout/api/Dockerfile

FROM python:3.10-slim

# Set the single working directory for the application
WORKDIR /app

# Copy and install requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into /app
COPY . .

# EXPOSE the port the app runs on
EXPOSE 8000

# Run uvicorn from the /app directory, where main.py is located
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]