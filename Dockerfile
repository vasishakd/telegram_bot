FROM python:3.12.11-slim

WORKDIR /opt
ENV PYTHONPATH=/opt
ENV NVM_DIR /root/nvm
ENV NODE_VERSION 18

COPY . .

RUN apt-get update && apt-get install -y \
       curl \
       git \
       build-essential

RUN mkdir "$NVM_DIR" && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash

RUN . "$NVM_DIR/nvm.sh" && \
    nvm install "$NODE_VERSION" && \
    nvm use "$NODE_VERSION" && \
    nvm alias default "$NODE_VERSION"

ENV NODE_PATH $NVM_DIR/versions/node/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

RUN  pip install --upgrade pip && \
     pip install uv && \
     uv export > requirements.txt && \
     uv pip install -r requirements.txt --system
