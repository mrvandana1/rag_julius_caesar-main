
# FROM python:3.11-slim AS builder

# WORKDIR /app

# RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# # Stage 2: Final lightweight image
# FROM python:3.11-slim

# WORKDIR /app

# COPY --from=builder /install /usr/local

# COPY . .

# EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "backend_app.py"]
