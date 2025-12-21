FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY main.py .
COPY model_installer.py .

RUN pip install -r requirements.txt

RUN python model_installer.py

ENTRYPOINT ["python", "main.py"]