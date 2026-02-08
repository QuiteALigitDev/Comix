FROM python:3.12-slim

WORKDIR /comix

RUN apt update && apt install -y unrar-free curl && rm -rf /var/lib/apt/lists/*

RUN curl -L https://raw.githubusercontent.com/QuiteALigitDev/Comix/refs/heads/main/requirements.txt -o requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN curl -L  https://raw.githubusercontent.com/QuiteALigitDev/Comix/refs/heads/main/main.py -o main.py

EXPOSE 5000

CMD ["python", "main.py", "-d", "/home/sh", "-p", "5000"]