FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    fonts-noto-color-emoji \
    fonts-dejavu \
    fonts-kacst \
    fonts-kacst-one \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY professeur_agent_FINAL.py .

CMD ["python", "professeur_agent_FINAL.py"]
