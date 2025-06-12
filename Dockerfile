FROM python:3.12.11-slim

WORKDIR /opt
ENV PYTHONPATH=/opt

COPY . .

RUN  pip install --upgrade pip && \
     pip install uv && \
     uv export > requirements.txt && \
     uv pip install -r requirements.txt --system
