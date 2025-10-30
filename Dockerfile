FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY venom/ ./venom/
COPY main.py .
COPY setup.py .

# Install package
RUN pip install -e .

# Expose metrics port
EXPOSE 8000

# Run Arbiter with infinite beats
CMD ["python", "main.py", "--beats", "-1"]
