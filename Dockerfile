FROM python:3.9-slim

WORKDIR /app

# Copie des scripts
COPY server.py /app/server.py
COPY client.py /app/client.py

ENV SERVER_IP=localhost
ENV CLIENT_ID=Client_X

CMD ["python", "server.py"]
