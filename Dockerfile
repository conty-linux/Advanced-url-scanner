FROM kalilinux/kali-rolling

# Install system dependencies
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    nmap \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p logs exports data

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_ENV=production

# Run the application
CMD ["python3", "backend/app.py", "--server", "--host", "0.0.0.0", "--port", "5000"]
