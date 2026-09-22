FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

# Télécharge les modèles nécessaires (ex. VAD Silero) au moment du build
RUN python agent.py download-files

CMD ["python", "agent.py", "start"]
