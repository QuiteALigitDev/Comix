FROM python:3.12-slim

WORKDIR /app

RUN apt update && apt install -y unrar-free curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 5000

CMD ["python", "main.py", "-d", "/home/sh", "-p", "5000"]
