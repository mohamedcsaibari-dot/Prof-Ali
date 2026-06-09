FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Africa/Casablanca

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    fonts-noto-color-emoji \
    fonts-dejavu \
    fonts-kacst \
    fonts-kacst-one \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY professeur_agent_FINAL.py .

CMD ["python3", "professeur_agent_FINAL.py"]
