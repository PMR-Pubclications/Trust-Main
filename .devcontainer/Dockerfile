FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

COPY asset/py/ferensics-ai/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt debugpy \
  && rm /tmp/requirements.txt
