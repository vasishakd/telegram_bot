FROM python:3.12.11-slim

WORKDIR /opt
ENV PYTHONPATH=/opt

COPY . .

RUN  apt update && \
     apt install -y curl build-essential && \
     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash && \
     nvm install 18 && \
     nvm use 18 && \
     pip install --upgrade pip && \
     pip install uv && \
     uv export > requirements.txt && \
     uv pip install -r requirements.txt --system
