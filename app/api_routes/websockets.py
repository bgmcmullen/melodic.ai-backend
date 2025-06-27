from fastapi import APIRouter, WebSocket
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.services.transcriber import transcribe_pitch

websocket_router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

@websocket_router.get("/ws/pitch")
async def pitch_websocket(websocket: WebSocket):
  await websocket.accept()

  while True:
    try:
      audio_chunk = await websocket.recieve_bytes()

      loop = asyncio.get_running_loop()
      notes = await loop.run_in_executor(executor, transcribe_pitch, audio_chunk)

      await websocket.send_json({"notes": notes})

    except Exception as e:
      await websocket.close()
      break