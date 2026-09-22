# Agent vocal LiveKit

Agent vocal conversationnel bâti sur le SDK LiveKit Agents.

- STT : Deepgram (nova-3)
- LLM : Groq (llama-3.3-70b-versatile)
- TTS : Cartesia (sonic-2)
- VAD : Silero

## Lancer en local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis remplis tes clés
python agent.py download-files
python agent.py console   # mode test dans le terminal, avec micro
```

## Tester avec le téléphone (mobile)

```bash
python agent.py dev
```

Puis ouvre https://agents-playground.livekit.io sur le navigateur du téléphone,
connecte-toi avec l'URL et les clés de ton projet LiveKit, et parle à l'agent.

## Déploiement (Render / Fly.io)

Ce repo inclut un `Dockerfile`. Sur Render ou Fly.io :
1. Crée un nouveau service à partir de ce repo GitHub.
2. Renseigne les variables d'environnement (mêmes noms que `.env.example`).
3. Déploie — le `Dockerfile` s'occupe du reste.
