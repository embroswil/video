import logging
import os

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    MetricsCollectedEvent,
    RunContext,
    cli,
    metrics,
    room_io,
)
from livekit.agents.llm import function_tool
from livekit.plugins import cartesia, deepgram, groq, silero, simli

logger = logging.getLogger("voice-agent")

load_dotenv()


class MyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "Tu es un assistant vocal amical et serviable. "
                "Garde tes réponses courtes et naturelles, comme dans une vraie conversation orale. "
                "N'utilise jamais d'emojis, d'astérisques, de markdown ou d'autres caractères spéciaux "
                "dans tes réponses, car elles seront lues à voix haute. "
                "Réponds en français, sauf si l'utilisateur te parle dans une autre langue."
            ),
        )

    async def on_enter(self) -> None:
        self.session.generate_reply(
            instructions="Salue l'utilisateur brièvement et demande-lui comment tu peux l'aider."
        )

    @function_tool
    async def get_current_time(self, context: RunContext) -> str:
        """Appelée quand l'utilisateur demande l'heure actuelle."""
        import datetime

        now = datetime.datetime.now().strftime("%H:%M")
        return f"Il est {now}."


server = AgentServer()


@server.rtc_session(agent_name="video-agent")
async def entrypoint(ctx: JobContext) -> None:
    ctx.log_context_fields = {"room": ctx.room.name}

    session: AgentSession = AgentSession(
        # Speech-to-text : les oreilles de l'agent (Deepgram)
        stt=deepgram.STT(model="nova-3", language="multi"),
        # LLM : le cerveau de l'agent (Groq, inférence rapide et gratuite)
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        # Text-to-speech : la voix de l'agent (Cartesia)
        tts=cartesia.TTS(
            model="sonic-2",
            voice="e07c00bc-4134-4eae-9ea4-1a55fb45746b",  # voix par défaut, changeable
        ),
        # Détection d'activité vocale (silence/parole)
        vad=silero.VAD.load(),
    )

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent) -> None:
        if ev.metrics.type == "stt_metrics":
            return
        metrics.log_metrics(ev.metrics)

    async def log_usage() -> None:
        logger.info(f"Usage: {session.usage}")

    ctx.add_shutdown_callback(log_usage)

    avatar = simli.AvatarSession(
        simli_config=simli.SimliConfig(
            api_key=os.getenv("SIMLI_API_KEY"),
            face_id=os.getenv("SIMLI_FACE_ID"),
        ),
    )
    await avatar.start(session, room=ctx.room)

    await session.start(
        agent=MyAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(server)
