# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Copy requirements (if you have a requirements.txt) or install inline
# For your project, install required Python packages
RUN pip install -r requirements.txt

# Expose the port Uvicorn will run on
EXPOSE 8000

# Set environment variables (optional)
# ENV OPENAI_API_KEY=your_openai_key
# ENV OPENAI_API_BASE=https://api.openai.com/v1
# ENV GROQ_API_KEY=your_groq_key

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
