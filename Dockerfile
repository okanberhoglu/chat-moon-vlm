FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY main.py .
COPY config.py .
COPY ui ./ui
COPY services ./services
COPY model ./model

RUN pip install -r requirements.txt

RUN python ./model/model_installer.py

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]