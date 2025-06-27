from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.services.transcriber import transcribe_pitch

websocket_router = APIRouter()
executor = ThreadPoolExecutor(max_workers=10)


async def process_chunk(audio_chunk: bytes, websocket: WebSocket, loop: asyncio.AbstractEventLoop):
    notes = await loop.run_in_executor(executor, transcribe_pitch, audio_chunk)
    await websocket.send_json({"notes": notes})

@websocket_router.websocket("/pitch")
async def pitch_websocket(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_running_loop()

    try:
      while True:
        audio_chunk = await websocket.receive_bytes()

        asyncio.create_task(process_chunk(audio_chunk, websocket, loop))

    except WebSocketDisconnect:
        print("❎ WebSocket client disconnected")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")